# YouTube Stock Videos Feature

This feature allows users to search for stock-related videos on YouTube and save them for later viewing.

## Features

- **Search YouTube for Stock Videos**: Users can search for stock market, investing, and financial videos.
- **Save Videos for Later**: Users can save videos they want to watch later.
- **Add Notes to Saved Videos**: Users can add personal notes to their saved videos.
- **Manage Saved Videos**: Users can view, update notes on, and delete their saved videos.

## Setup Requirements

1. A YouTube Data API key from Google Cloud Console.
2. Add the API key to your `.env` file as `YOUTUBE_API=your_api_key_here`.

## API Endpoints

### YouTube Videos

- `GET /youtube/videos/search/?q=query` - Search for videos on YouTube
- `GET /youtube/videos/` - List cached YouTube videos in the database

### Saved Videos

- `GET /youtube/saved/` - List all videos saved by the current user
- `GET /youtube/saved/<id>/` - Get a specific saved video
- `POST /youtube/saved/` - Save a video to watch later
- `PATCH /youtube/saved/<id>/` - Update notes on a saved video
- `DELETE /youtube/saved/<id>/` - Remove a video from saved list
- `GET /youtube/saved/my_saved_videos/` - Get all videos saved by current user (alternative endpoint)

## Frontend Routes

- `/youtube/search` - Search YouTube for stock videos
- `/youtube/saved` - View and manage saved videos

## Testing the API

You can test the YouTube API integration using the provided management command:

```bash
python manage.py test_youtube_api "stock market" --results=5
```

## Troubleshooting

- **API Quota Limits**: YouTube Data API has daily quota limits. Monitor your usage in the Google Cloud Console.
- **API Key Issues**: Make sure your API key is correctly set in the `.env` file and has the proper permissions.
- **Video Not Found**: If a video was deleted from YouTube, it may still exist in your saved list but won't be accessible on YouTube.
