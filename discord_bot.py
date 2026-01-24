from discord_webhook import DiscordWebhook, DiscordEmbed
import time

def send_report(webhook_url, content, title="Political News Report"):
    """
    Sends a report to Discord via Webhook.
    Handles long messages by splitting.
    """
    if not webhook_url:
        print("Error: No Webhook URL provided.")
        return

    # Discord limit is 2000 chars per message content, or 4096 for embed description.
    # We use Embeds for nicer formatting.
    
    # Split content if too long
    # Simple split by chunks
    chunk_size = 4000
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    
    for i, chunk in enumerate(chunks):
        webhook = DiscordWebhook(url=webhook_url)
        embed = DiscordEmbed(title=f"{title} ({i+1}/{len(chunks)})" if len(chunks) > 1 else title,
                             description=chunk, color='03b2f8')
        webhook.add_embed(embed)
        response = webhook.execute()
        time.sleep(1) # Rate limit

if __name__ == "__main__":
    # Test (Replace with real URL if needed for verify)
    pass
