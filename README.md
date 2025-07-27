# Pi-hole DNS Blocklists

A curated collection of DNS blocklists and allowlists for Pi-hole, designed to work with [pihole-updatelists](https://github.com/jacklul/pihole-updatelists) for automated list management.

## Overview

This repository contains:
- **Blocklists**: DNS blocklists targeting ads, malware, tracking, and unwanted content
- **Allowlists**: Carefully curated domains that should never be blocked
- **Regex patterns**: Advanced filtering rules for specific use cases

## Usage with pihole-updatelists

1. Install [pihole-updatelists](https://github.com/jacklul/pihole-updatelists)
2. Clone this repository to your Pi-hole server
3. Create or update your `pihole-updatelists.conf` file:

```bash
# /etc/pihole-updatelists.conf

ADLISTS_URL="file:///path/to/dns-blocklists/blocklists.txt"
WHITELIST_URL="file:///path/to/dns-blocklists/allowlists.txt"
WHITELIST_EXACT_URL="file:///path/to/dns-blocklists/allowlist.txt"
REGEX_WHITELIST_URL="file:///path/to/dns-blocklists/regex-allowlist.txt"
```

4. Run pihole-updatelists to apply the configuration:
```bash
pihole-updatelists
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