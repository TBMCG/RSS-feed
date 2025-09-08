"""
Custom RSS parser that works with Python 3.13+
Replaces feedparser which has compatibility issues with Python 3.13
"""

import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from html import unescape
import re

class RSSParser:
    """Simple RSS feed parser compatible with Python 3.13+"""
    
    @staticmethod
    def parse(url):
        """Parse RSS feed from URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return RSSParser.parse_string(response.text)
        except Exception as e:
            print(f"Error fetching RSS feed: {e}")
            return {'entries': []}
    
    @staticmethod
    def parse_string(xml_content):
        """Parse RSS feed from XML string"""
        try:
            root = ET.fromstring(xml_content)
            
            # Handle both RSS 2.0 and Atom feeds
            if root.tag == 'rss' or 'rss' in root.tag:
                return RSSParser._parse_rss(root)
            elif 'feed' in root.tag.lower() or 'atom' in xml_content[:100].lower():
                return RSSParser._parse_atom(root)
            else:
                # Try RSS parsing as default
                return RSSParser._parse_rss(root)
                
        except Exception as e:
            print(f"Error parsing RSS feed: {e}")
            return {'entries': []}
    
    @staticmethod
    def _parse_rss(root):
        """Parse RSS 2.0 feed"""
        entries = []
        
        # Find the channel element
        channel = root.find('channel')
        if channel is None:
            channel = root
        
        # Parse items
        for item in channel.findall('item'):
            entry = {
                'title': RSSParser._get_text(item, 'title'),
                'link': RSSParser._get_text(item, 'link'),
                'description': RSSParser._clean_html(RSSParser._get_text(item, 'description')),
                'summary': RSSParser._clean_html(RSSParser._get_text(item, 'description')),
                'published': RSSParser._get_text(item, 'pubDate'),
                'author': RSSParser._get_text(item, 'author') or RSSParser._get_text(item, 'dc:creator'),
                'guid': RSSParser._get_text(item, 'guid'),
            }
            
            # Parse categories
            categories = []
            for cat in item.findall('category'):
                if cat.text:
                    categories.append(cat.text)
            entry['categories'] = categories
            
            entries.append(entry)
        
        return {
            'entries': entries,
            'feed': {
                'title': RSSParser._get_text(channel, 'title'),
                'link': RSSParser._get_text(channel, 'link'),
                'description': RSSParser._get_text(channel, 'description'),
            }
        }
    
    @staticmethod
    def _parse_atom(root):
        """Parse Atom feed"""
        entries = []
        
        # Define Atom namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # Parse entries
        for entry in root.findall('.//atom:entry', ns) or root.findall('.//entry'):
            item = {
                'title': RSSParser._get_text(entry, 'title') or RSSParser._get_text(entry, '{http://www.w3.org/2005/Atom}title'),
                'link': '',
                'description': '',
                'summary': '',
                'published': RSSParser._get_text(entry, 'published') or RSSParser._get_text(entry, 'updated'),
                'author': '',
                'guid': RSSParser._get_text(entry, 'id'),
            }
            
            # Get link
            link_elem = entry.find('link') or entry.find('{http://www.w3.org/2005/Atom}link')
            if link_elem is not None:
                item['link'] = link_elem.get('href', '')
            
            # Get content/summary
            content = RSSParser._get_text(entry, 'content') or RSSParser._get_text(entry, 'summary')
            if not content:
                content = RSSParser._get_text(entry, '{http://www.w3.org/2005/Atom}content') or RSSParser._get_text(entry, '{http://www.w3.org/2005/Atom}summary')
            
            item['description'] = RSSParser._clean_html(content)
            item['summary'] = item['description']
            
            # Get author
            author_elem = entry.find('author') or entry.find('{http://www.w3.org/2005/Atom}author')
            if author_elem is not None:
                item['author'] = RSSParser._get_text(author_elem, 'name') or RSSParser._get_text(author_elem, '{http://www.w3.org/2005/Atom}name')
            
            entries.append(item)
        
        return {
            'entries': entries,
            'feed': {
                'title': RSSParser._get_text(root, 'title') or RSSParser._get_text(root, '{http://www.w3.org/2005/Atom}title'),
                'link': '',
                'description': RSSParser._get_text(root, 'subtitle') or RSSParser._get_text(root, '{http://www.w3.org/2005/Atom}subtitle'),
            }
        }
    
    @staticmethod
    def _get_text(parent, tag):
        """Safely get text from an XML element"""
        if parent is None:
            return ''
        
        elem = parent.find(tag)
        if elem is None and ':' not in tag:
            # Try with common namespaces
            for ns_tag in [f'{{http://www.w3.org/2005/Atom}}{tag}', 
                          f'{{http://purl.org/dc/elements/1.1/}}{tag}']:
                elem = parent.find(ns_tag)
                if elem is not None:
                    break
        
        if elem is not None and elem.text:
            return elem.text.strip()
        return ''
    
    @staticmethod
    def _clean_html(html_text):
        """Remove HTML tags and decode entities"""
        if not html_text:
            return ''
        
        # Remove HTML tags
        clean_text = re.sub('<[^<]+?>', '', html_text)
        
        # Decode HTML entities
        clean_text = unescape(clean_text)
        
        # Clean up whitespace
        clean_text = ' '.join(clean_text.split())
        
        return clean_text.strip()

# Create a feedparser-compatible interface
def parse(url_or_string):
    """Parse RSS feed from URL or XML string - feedparser compatible interface"""
    if url_or_string.startswith('http'):
        return RSSParser.parse(url_or_string)
    else:
        return RSSParser.parse_string(url_or_string)