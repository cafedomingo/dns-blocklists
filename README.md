# Pi-hole DNS Blocklists

A curated collection of DNS blocklists and allowlists for Pi-hole, designed to work with [pihole-updatelists](https://github.com/jacklul/pihole-updatelists) for automated list management.

## Overview

This repository contains:
- **Blocklists**: DNS blocklists targeting ads, malware, tracking, and unwanted content
- **Allowlists**: Carefully curated domains that should never be blocked
- **Regex patterns**: Advanced filtering rules for specific use cases

## Usage with pihole-updatelists

1. Install [pihole-updatelists](https://github.com/jacklul/pihole-updatelists)
2. Create or update your `pihole-updatelists.conf` file:

```bash
# /etc/pihole-updatelists.conf
# See: https://github.com/jacklul/pihole-updatelists#configuration

ALLOWLISTS_URL="https://raw.githubusercontent.com/cafedomingo/dns-blocklists/main/allowlists.txt"
BLACKLIST_URL="https://raw.githubusercontent.com/cafedomingo/dns-blocklists/main/blocklist.txt"
BLOCKLISTS_URL="https://raw.githubusercontent.com/cafedomingo/dns-blocklists/main/blocklists.txt"
REGEX_BLACKLIST_URL="https://raw.githubusercontent.com/cafedomingo/dns-blocklists/main/regex-blocklist.txt"
REGEX_WHITELIST_URL="https://raw.githubusercontent.com/cafedomingo/dns-blocklists/main/regex-allowlist.txt"
WHITELIST_URL="https://raw.githubusercontent.com/cafedomingo/dns-blocklists/main/allowlist.txt"
```

3. Run pihole-updatelists to apply the configuration:
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