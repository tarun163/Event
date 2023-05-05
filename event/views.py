from django.shortcuts import redirect
from django.views import View
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.http import JsonResponse, HttpResponseServerError
from .settings import CLIENT_ID, CLIENT_SECRET, SCOPES


class GoogleCalendarInitView(View):
    def get(self, request):
        # Set up the OAuth2 flow
        flow = Flow.from_client_config(
            client_config={
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uris': ['http://127.0.0.1:8000/rest/v1/calendar/redirect/']
            },
            scopes=SCOPES,
            authorization_prompt_message='Please authenticate with Google to access your calendar'
        )

        # authorization URL redirect the user
        authorization_url, _ = flow.authorization_url(prompt='consent')
        return redirect(authorization_url)


class GoogleCalendarRedirectView(View):
    def get(self, request):
        
        # code from the redirect URL
        code = request.GET.get('code')

        # for fetch the athentication code from code by google 
        flow = Flow.from_client_config(
            client_config={
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uris': ['http://127.0.0.1:8000/rest/v1/calendar/redirect/']
            },
            scopes=SCOPES
        )
        flow.fetch_token(code=code)

        # access token requests to the Google Calendar API
        credentials = Credentials.from_authorized_user_info(info=flow.credentials.to_json())
        service = build('calendar', 'v3', credentials=credentials)

        # Retrieve the user's calendar events
        try:
            events = service.events().list(calendarId='primary', maxResults=10).execute()
            return JsonResponse(events)
        except HttpError as error:
            return HttpResponseServerError(f'An error occurred: {error}')
