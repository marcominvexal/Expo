"""Small HTML notices shown while a sync is running."""


def gemini_retry_wait_html(remaining_seconds, total_timeout_left):
    """Status line shown while waiting to retry a busy Gemini model."""
    return f"""
    <div class="retry-notice" role="status">
        <span class="retry-dot"></span>
        <span><strong>Gemini is busy.</strong> Retrying in {remaining_seconds}s
        &middot; the sync stops after {total_timeout_left}s more, and any unprocessed emails stay unread.</span>
    </div>
    """
