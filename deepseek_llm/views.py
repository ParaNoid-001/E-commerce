from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils.safestring import mark_safe
import markdown
from .forms import QueryForm
from .langchain import askQuery
from django.conf import settings

# class AskQueryView(View):
#     def get(self, request):
#         return render(request, 'deepseek_llm/deepseek_llm.html')

#     def post(self, request):
#         form = QueryForm(request.POST)
#         if form.is_valid():
#             query = form.cleaned_data['query']
#             response = askQuery(query)
            
#             # Convert response to Markdown with syntax highlighting
#             markdown_response = mark_safe(markdown.markdown(
#                 response,
#                 extensions=['fenced_code', 'codehilite']
#             ))
            
#             return JsonResponse({'ai_content': markdown_response})
        
#         return JsonResponse({'error': 'Invalid form'}, status=400)

from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
import markdown
from .forms import QueryForm
from .langchain import askQuery
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class AskQueryView(View):
    def get(self, request):
        """Handle both full page and AJAX GET requests"""
        form = QueryForm()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Return just the form HTML for AJAX requests
            return render(request, 'deepseek_llm/partials/ai_assistant_form.html', {
                'form': form
            })
            
        return render(request, 'deepseek_llm/deepseek_llm.html', {
            'form': form,
            'is_ajax': request.headers.get('x-requested-with') == 'XMLHttpRequest'
        })

    @lru_cache(maxsize=128)  # Cache common queries
    def post(self, request):
        """Handle AJAX POST requests for query processing"""
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            logger.warning('Non-AJAX request received')
            return JsonResponse({
                'error': 'This endpoint only accepts AJAX requests',
                'status': 'error'
            }, status=400)

        form = QueryForm(request.POST)
        if not form.is_valid():
            logger.debug('Form validation failed: %s', form.errors)
            return JsonResponse({
                'error': 'Invalid input',
                'details': form.errors.get_json_data(),
                'status': 'error'
            }, status=400)

        try:
            query = form.cleaned_data['query'].strip()
            logger.info('Processing query: %s', query[:50])  # Log first 50 chars
            
            # Process query with rate limiting consideration
            response = self._get_ai_response(query)
            
            markdown_response = mark_safe(markdown.markdown(
                response,
                extensions=['fenced_code', 'codehilite'],
                extension_configs={
                    'codehilite': {
                        'linenums': False,
                        'guess_lang': True,
                        'css_class': 'highlight'
                    }
                }
            ))
            
            return JsonResponse({
                'ai_content': markdown_response,
                'status': 'success',
                'query': query[:100]  # Return truncated query for reference
            })
            
        except Exception as e:
            logger.error('Error processing query: %s', str(e), exc_info=True)
            return JsonResponse({
                'error': 'An error occurred while processing your request',
                'status': 'error',
                'debug': str(e) if settings.DEBUG else None
            }, status=500)

    def _get_ai_response(self, query):
        """Wrapper method for AI response generation with error handling"""
        try:
            return askQuery(query)
        except ConnectionError as e:
            logger.error('Connection error with AI service: %s', str(e))
            return "⚠️ Our AI service is currently unavailable. Please try again later."
        except TimeoutError:
            logger.error('Timeout from AI service')
            return "⚠️ The request timed out. Please try a simpler query or try again later."
        except Exception as e:
            logger.error('Unexpected error from AI service: %s', str(e))
            return f"⚠️ An error occurred: {str(e)}"