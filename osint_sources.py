import requests
import trafilatura
import socket
import json
import re
from urllib.parse import urlparse
from datetime import datetime
import time

class OSINTCollector:
    """Main class for collecting OSINT data from various sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def collect_data(self, source_type, target):
        """Main method to collect data based on source type"""
        try:
            if source_type == 'website':
                return self._collect_website_data(target)
            elif source_type == 'dns':
                return self._collect_dns_data(target)
            elif source_type == 'whois':
                return self._collect_whois_data(target)
            elif source_type == 'social_media':
                return self._collect_social_media_data(target)
            elif source_type == 'email':
                return self._collect_email_data(target)
            elif source_type == 'ip':
                return self._collect_ip_data(target)
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
        except Exception as e:
            return {
                'error': str(e),
                'source_url': '',
                'data': {},
                'metadata': {'error': str(e), 'timestamp': datetime.utcnow().isoformat()},
                'confidence_score': 0.0
            }
    
    def _collect_website_data(self, url):
        """Collect data from a website using web scraping"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Get main content using trafilatura
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                raise Exception("Failed to fetch website content")
            
            text_content = trafilatura.extract(downloaded)
            metadata_content = trafilatura.extract_metadata(downloaded)
            
            # Get additional page information
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Extract basic information
            page_info = {
                'title': metadata_content.title if metadata_content and metadata_content.title else 'Unknown',
                'description': metadata_content.description if metadata_content and metadata_content.description else '',
                'author': metadata_content.author if metadata_content and metadata_content.author else '',
                'date': metadata_content.date if metadata_content and metadata_content.date else '',
                'text_content': text_content[:1000] if text_content else '',  # Limit content length
                'content_length': len(text_content) if text_content else 0,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'server': response.headers.get('server', ''),
                'last_modified': response.headers.get('last-modified', ''),
                'language': metadata_content.language if metadata_content and metadata_content.language else ''
            }
            
            # Extract links and emails from content
            if text_content:
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = list(set(re.findall(email_pattern, text_content)))
                page_info['emails_found'] = emails[:10]  # Limit to 10 emails
            
            return {
                'source_url': url,
                'data': page_info,
                'metadata': {
                    'collection_time': datetime.utcnow().isoformat(),
                    'method': 'web_scraping',
                    'response_time': response.elapsed.total_seconds()
                },
                'confidence_score': 0.8 if text_content else 0.3
            }
            
        except Exception as e:
            raise Exception(f"Website data collection failed: {str(e)}")
    
    def _collect_dns_data(self, domain):
        """Collect DNS information for a domain"""
        try:
            dns_info = {}
            
            # Remove protocol if present
            domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
            
            # Get different DNS record types
            record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME']
            
            for record_type in record_types:
                try:
                    if record_type == 'A':
                        result = socket.gethostbyname_ex(domain)
                        dns_info[record_type] = result[2]  # IP addresses
                    elif record_type == 'AAAA':
                        # IPv6 lookup (simplified)
                        try:
                            result = socket.getaddrinfo(domain, None, socket.AF_INET6)
                            dns_info[record_type] = list(set([r[4][0] for r in result]))
                        except:
                            dns_info[record_type] = []
                    else:
                        # For other record types, we'll use a simplified approach
                        dns_info[record_type] = []
                except:
                    dns_info[record_type] = []
            
            # Get basic domain info
            try:
                host_info = socket.gethostbyname_ex(domain)
                dns_info['canonical_name'] = host_info[0]
                dns_info['aliases'] = host_info[1]
            except:
                dns_info['canonical_name'] = domain
                dns_info['aliases'] = []
            
            return {
                'source_url': f"dns://{domain}",
                'data': dns_info,
                'metadata': {
                    'collection_time': datetime.utcnow().isoformat(),
                    'method': 'dns_lookup',
                    'domain': domain
                },
                'confidence_score': 0.9 if dns_info.get('A') else 0.2
            }
            
        except Exception as e:
            raise Exception(f"DNS data collection failed: {str(e)}")
    
    def _collect_whois_data(self, domain):
        """Collect WHOIS information (simplified version)"""
        try:
            # Remove protocol if present
            domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
            
            # This is a simplified WHOIS implementation
            # In a production environment, you would use a proper WHOIS library
            whois_info = {
                'domain': domain,
                'status': 'active',
                'note': 'WHOIS data collection requires specialized libraries for full functionality'
            }
            
            # Try to get basic domain info
            try:
                ip = socket.gethostbyname(domain)
                whois_info['resolved_ip'] = ip
            except:
                whois_info['resolved_ip'] = 'Unable to resolve'
            
            return {
                'source_url': f"whois://{domain}",
                'data': whois_info,
                'metadata': {
                    'collection_time': datetime.utcnow().isoformat(),
                    'method': 'whois_lookup',
                    'note': 'Simplified WHOIS implementation'
                },
                'confidence_score': 0.5
            }
            
        except Exception as e:
            raise Exception(f"WHOIS data collection failed: {str(e)}")
    
    def _collect_social_media_data(self, query):
        """Collect social media information (public data only)"""
        try:
            # This is a placeholder for social media data collection
            # In a real implementation, you would use official APIs
            social_info = {
                'query': query,
                'platforms_searched': ['Twitter', 'LinkedIn', 'GitHub'],
                'note': 'Social media data collection requires API keys and proper authentication',
                'public_mentions': [],
                'profiles_found': []
            }
            
            # For demonstration, we'll search for GitHub profiles
            try:
                github_url = f"https://github.com/{query}"
                response = self.session.get(github_url, timeout=5)
                if response.status_code == 200:
                    social_info['github_profile'] = github_url
                    social_info['github_exists'] = True
                else:
                    social_info['github_exists'] = False
            except:
                social_info['github_exists'] = False
            
            return {
                'source_url': f"social://{query}",
                'data': social_info,
                'metadata': {
                    'collection_time': datetime.utcnow().isoformat(),
                    'method': 'social_media_search',
                    'note': 'Limited implementation - requires API access for full functionality'
                },
                'confidence_score': 0.3
            }
            
        except Exception as e:
            raise Exception(f"Social media data collection failed: {str(e)}")
    
    def _collect_email_data(self, email):
        """Collect email-related information"""
        try:
            email_info = {
                'email': email,
                'domain': email.split('@')[1] if '@' in email else '',
                'local_part': email.split('@')[0] if '@' in email else email,
                'valid_format': '@' in email and '.' in email.split('@')[1] if '@' in email else False
            }
            
            # Check if domain exists
            if email_info['domain']:
                try:
                    socket.gethostbyname(email_info['domain'])
                    email_info['domain_exists'] = True
                except:
                    email_info['domain_exists'] = False
            
            return {
                'source_url': f"email://{email}",
                'data': email_info,
                'metadata': {
                    'collection_time': datetime.utcnow().isoformat(),
                    'method': 'email_analysis'
                },
                'confidence_score': 0.7 if email_info['valid_format'] else 0.2
            }
            
        except Exception as e:
            raise Exception(f"Email data collection failed: {str(e)}")
    
    def _collect_ip_data(self, ip):
        """Collect IP address information"""
        try:
            ip_info = {
                'ip_address': ip,
                'type': 'IPv4' if '.' in ip else 'IPv6' if ':' in ip else 'Unknown'
            }
            
            # Try reverse DNS lookup
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                ip_info['hostname'] = hostname
            except:
                ip_info['hostname'] = 'No reverse DNS'
            
            # Basic IP validation
            try:
                socket.inet_aton(ip)  # IPv4 validation
                ip_info['valid_ipv4'] = True
            except:
                ip_info['valid_ipv4'] = False
            
            return {
                'source_url': f"ip://{ip}",
                'data': ip_info,
                'metadata': {
                    'collection_time': datetime.utcnow().isoformat(),
                    'method': 'ip_analysis'
                },
                'confidence_score': 0.8 if ip_info.get('valid_ipv4') else 0.4
            }
            
        except Exception as e:
            raise Exception(f"IP data collection failed: {str(e)}")
