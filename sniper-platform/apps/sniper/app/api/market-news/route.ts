import { NextResponse } from 'next/server';

export const revalidate = 0;
export const dynamic = 'force-dynamic';

interface NewsItem {
  title: string;
  link: string;
  source: string;
  pubDate: string;
  relativeTime: string;
}

function extractCDATA(text: string): string {
  const match = text.match(/<!\[CDATA\[(.*?)\]\]>/s);
  return match ? match[1].trim() : text.trim();
}

function extractTagContent(xml: string, tag: string): string {
  const regex = new RegExp(`<${tag}[^>]*>(.*?)</${tag}>`, 's');
  const match = xml.match(regex);
  return match ? match[1] : '';
}

function relativeTime(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  if (isNaN(then)) return '';
  const diffMin = Math.floor((now - then) / 60000);
  if (diffMin < 1) return 'Just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  return `${diffDay}d ago`;
}

function parseSource(title: string): { cleanTitle: string; source: string } {
  const match = title.match(/^(.*)\s*-\s*([^-]+)$/);
  if (match) {
    return { cleanTitle: match[1].trim(), source: match[2].trim() };
  }
  return { cleanTitle: title, source: 'News' };
}

async function fetchGoogleNewsRSS(query: string): Promise<NewsItem[]> {
  const url = `https://news.google.com/rss/search?q=${encodeURIComponent(query)}&hl=en-IN&gl=IN&ceid=IN:en`;
  const res = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' },
    next: { revalidate: 0 },
  });
  if (!res.ok) return [];
  const xml = await res.text();

  const items: NewsItem[] = [];
  const itemRegex = /<item>(.*?)<\/item>/gs;
  let match;
  while ((match = itemRegex.exec(xml)) !== null) {
    const itemXml = match[1];
    const rawTitle = extractCDATA(extractTagContent(itemXml, 'title'));
    const link = extractCDATA(extractTagContent(itemXml, 'link'));
    const pubDate = extractTagContent(itemXml, 'pubDate');
    const { cleanTitle, source } = parseSource(rawTitle);
    items.push({
      title: cleanTitle,
      link,
      source,
      pubDate,
      relativeTime: relativeTime(pubDate),
    });
  }
  return items;
}

export async function GET() {
  try {
    const [niftyNews, marketNews, rbiNews] = await Promise.all([
      fetchGoogleNewsRSS('NIFTY 50 stock market India'),
      fetchGoogleNewsRSS('Indian stock market BSE NSE today'),
      fetchGoogleNewsRSS('RBI monetary policy India economy'),
    ]);

    const seen = new Set<string>();
    const allNews: NewsItem[] = [];
    for (const item of [...niftyNews, ...marketNews, ...rbiNews]) {
      const key = item.title.slice(0, 60).toLowerCase();
      if (!seen.has(key)) {
        seen.add(key);
        allNews.push(item);
      }
    }

    allNews.sort(
      (a, b) => new Date(b.pubDate).getTime() - new Date(a.pubDate).getTime(),
    );

    return NextResponse.json(
      { news: allNews.slice(0, 20), updatedAt: new Date().toISOString() },
      {
        headers: {
          'Cache-Control': 'public, s-maxage=120, stale-while-revalidate=600',
        },
      },
    );
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ news: [], error: message }, { status: 502 });
  }
}
