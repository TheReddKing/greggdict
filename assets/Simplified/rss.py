import feedparser

# Specify the URL of the RSS feed
feed_url = "http://example.com/rss_feed.xml"

# Parse the RSS feed
feed = feedparser.parse(feed_url)

# Check if the feed was successfully parsed
if feed.bozo == 0:
    # Iterate over the entries in the feed
    for entry in feed.entries:
        # Extract relevant information from each entry
        title = entry.title
        published_date = entry.published
        summary = entry.summary

        # Do something with the extracted data
        print("Title:", title)
        print("Published Date:", published_date)
        print("Summary:", summary)
        print("----------------------------------")
else:
    print("Error parsing the feed")