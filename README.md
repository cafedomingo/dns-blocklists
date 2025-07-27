# Pi-hole DNS Blocklists

A curated collection of DNS blocklists and allowlists for Pi-hole, designed to work with [pihole-updatelists](https://github.com/jacklul/pihole-updatelists) for automated list management.

## Overview

This repository contains:
- **Blocklists**: Comprehensive DNS blocklists targeting ads, malware, tracking, and unwanted content
- **Allowlists**: Carefully curated domains that should never be blocked
- **Regex patterns**: Advanced filtering rules for specific use cases

## Blocklists Included

### Primary Protection
- **HaGeZi Pro**: High-quality, comprehensive ad and tracker blocking
- **HaGeZi Threat Intelligence Feeds**: Malware and security threat protection
- **HaGeZi Most Abused TLDs**: Blocks spam-prone top-level domains
- **xRuffKez NRD**: Newly registered domains (14-day protection)

### Platform-Specific Blocking
- **Apple**: iOS/macOS telemetry and unwanted services
- **Amazon**: Device telemetry, shopping trackers, video ads
- **Microsoft**: Windows/Office telemetry and tracking
- **Samsung**: Smart TV and device telemetry
- **LG WebOS**: Smart TV ads and tracking
- **TikTok**: Fingerprinting and tracking protection

### Content Filtering
- **NSFW**: Adult content blocking
- **Gambling**: Gambling site protection
- **Dynamic DNS**: Blocks suspicious dynamic DNS services

## Allowlists

- **GoodnessJSON Community Allowlist**: Common false positives and essential services
- **HaGeZi Referral Allowlist**: Legitimate referral and affiliate links
- **Custom Allowlist**: Apple services, URL shorteners, and other essential domains

## Usage with pihole-updatelists

1. Install [pihole-updatelists](https://github.com/jacklul/pihole-updatelists)
2. Clone this repository or download the list files
3. Configure pihole-updatelists to use these files:

```bash
# Example configuration
pihole-updatelists --adlists-url "file:///path/to/blocklists.txt" \
                   --whitelist-url "file:///path/to/allowlists.txt" \
                   --whitelist-exact-url "file:///path/to/allowlist.txt" \
                   --regex-whitelist-url "file:///path/to/regex-allowlist.txt"
```

## File Structure

- `blocklists.txt` - URLs of remote blocklists for pihole-updatelists
- `allowlists.txt` - URLs of remote allowlists for pihole-updatelists  
- `allowlist.txt` - Individual domains to always allow
- `regex-allowlist.txt` - Regex patterns for advanced allowlist rules
- `blocklist.txt` - Individual domains to block (currently empty)
- `regex-blocklist.txt` - Regex patterns for blocking (currently empty)

## Maintenance

Lists are automatically updated by pihole-updatelists when configured. Manual updates can be triggered as needed.

## License

MIT License - see [LICENSE](LICENSE) file for details.