# PHINEAS - Profound HUMINT Intelligence Network & Enrichment Automated System

> *"Hey Ferb, I know what we're gonna do today!"* - Every OSINT investigation ever

**PHINEAS** is your one-stop OSINT automation framework that does all the intelligence gathering busywork for you. Like Phineas and Ferb's ambitious summer projects, we tackle massive reconnaissance challenges with creativity, thoroughness, and zero paid services required.

*Where's Perry? Probably gathering OSINT on Doofenshmirtz.*

---

## What Does This Thing Do?

PHINEAS automates intelligence gathering from **100% free** OSINT sources across the internet. No paid services, no credit cards, just pure reconnaissance goodness.

**Three workflows, one command:**
- **Email Intelligence** - "Hey, where's this email been?" (Breaches, accounts, social profiles)
- **Domain Reconnaissance** - "Ferb, I know what domain we're mapping today!" (Subdomains, emails, historical data)
- **Username Enumeration** - "Mom! Phineas is tracking someone across 300+ platforms!" (Social media hunting)

---

## Installation (It's Too Young to Drive, But It Can Run Itself)

### 1. Prerequisites
```bash
# Python 3.9+ (older than Candace's dating advice)
python --version

# Git clone or download this repo
cd D:\HAK\MasterOsint
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Free OSINT Tools

**Windows** (because even Candace uses Windows):
```bash
tools\install\install_tools.bat
```

**Linux/Mac** (for the cool kids):
```bash
chmod +x tools/install/install_tools.sh
./tools/install/install_tools.sh
```

**What gets installed:**
- Sherlock (300+ social networks)
- Holehe (120+ account checkers)
- theHarvester (email scraping)
- Sublist3r (subdomain hunting)
- Maigret (2500+ sites)
- h8mail (breach intelligence)

*"Yes. Yes, we are installing all of them."* - Ferb

---

## 🎮 Usage (Easier Than Building a Rollercoaster)

### Quick Start - Auto-Magic Detection

```bash
# PHINEAS automatically detects what you're scanning
python phineas.py scan --target john.doe@example.com
```

That's it! PHINEAS figures out you gave it an email and runs the email intelligence workflow. 

*"Aren't you a little young to be automating OSINT workflows?"*
*"Yes. Yes we are."*

### The Three Main Quests

**Email Intelligence**
```bash
python phineas.py scan --target victim@example.com

# Discovers:
# - Social media accounts (Holehe)
# - Data breaches (HaveIBeenPwned)
# - Username profiles (Sherlock)
# - Related emails (theHarvester)
```

**Domain Reconnaissance**
```bash
python phineas.py scan --target example.com

# Discovers:
# - Subdomains (Sublist3r)
# - Employee emails (theHarvester)
# - Historical snapshots (Wayback Machine)
# - And more!
```

**Username Hunt**
```bash
python phineas.py scan --target johndoe123

# Searches 300+ platforms:
# - Social media profiles
# - Gaming accounts
# - Developer platforms
# - Dating sites (yikes)
```

---

## ⚙️ Configuration (Like Perry's Secret Lair Button)

### Interactive Setup (Recommended)
```bash
python phineas.py setup
```
Walks you through everything. Even Candace could do it.

### Manual API Key Configuration
```bash
# Set a key
python phineas.py setkey haveibeenpwned YOUR_API_KEY

# Check what's configured
python phineas.py keys

# View available plugins
python phineas.py plugins

# See all workflows
python phineas.py workflows
```

### Free API Keys (No Credit Card, Unlike Mom's)

Most tools work WITHOUT API keys, but these add superpowers:

| Service | Free Tier | What It Does | Get Key |
|---------|-----------|--------------|---------|
| HaveIBeenPwned | Unlimited | Breach checking | [Get Key](https://haveibeenpwned.com/API/Key) |
| Shodan | 1/month | Internet device search | [Get Key](https://shodan.io) |
| SecurityTrails | 50/month | Historical DNS | [Get Key](https://securitytrails.com) |
| VirusTotal | 4 req/min | File/URL scanning | [Get Key](https://virustotal.com) |
| Hunter.io | 25/month | Email finder | [Get Key](https://hunter.io) |

*"The API keys are a lie!" - No wait, they're real and free.*

---

## Project Structure (More Organized Than Phineas's Backyard)

```
MasterOsint/
├── phineas.py              # Main CLI - "Hey Ferb!"
├── setup.py                # Package installer
├── requirements.txt        # Dependencies
├── README.md              # You are here
├── LICENSE                # MIT (Make It Tremendous)
├── .gitignore             # Git's Perry the Platypus
│
├── core/                  # The brains
│   ├── orchestrator.py    # Workflow conductor
│   ├── config_manager.py  # API keys & settings
│   └── result_aggregator.py  # Results smoosher
│
├── plugins/               # The tools
│   ├── people/           # Identity hunting
│   │   └── sherlock_plugin.py
│   ├── email/            # Email recon
│   │   ├── holehe_plugin.py
│   │   └── harvester_plugin.py
│   ├── breach/           # Breach intel
│   │   └── hibp_plugin.py
│   ├── domain/           # Domain mapping
│   │   └── sublist3r_plugin.py
│   └── passive/          # Sneaky stuff
│       └── wayback_plugin.py
│
├── workflows/             # Pre-built plans
│   ├── email_intelligence.yaml
│   ├── domain_reconnaissance.yaml
│   └── username_enumeration.yaml
│
├── integrations/          # Optional extras
│   └── cronos_bridge.py  # Cronos platform integration
│
├── config/               # Settings
│   └── phineas.yaml     # Main config
│
└── tools/                # Installation helpers
    └── install/
        ├── install_tools.sh
        └── install_tools.bat
```

---

## 🎨 Features (More Than Just a Backyard Attraction)

### ✨ What Makes PHINEAS Special

1. **100% Free** - No paid services. Mom doesn't even need to know.
2. **Auto-Detection** - Smarter than Candace's bust-catching strategies
3. **Plugin Architecture** - Modular like LEGO, but for OSINT
4. **Beautiful Output** - Rich terminal UI (not plain text like cavemen)
5. **Result Aggregation** - Deduplicates and scores findings
6. **Confidence Scoring** - "This finding has been confirmed by multiple sources"
7. **Workflow System** - Pre-built investigative workflows
8. **Standalone** - No cloud, no subscriptions, no surveillance capitalism

### Integrated Tools

| Category | Tools | What They Do |
|----------|-------|--------------|
| **People Intel** | Sherlock, Holehe, Maigret | Username hunting, email->account mapping |
| **Email Intel** | theHarvester, h8mail | Email harvesting, breach checking |
| **Breach Intel** | HaveIBeenPwned, Dehashed | Data breach detection |
| **Domain Intel** | Sublist3r, Amass, Shodan | Subdomain enumeration, exposed services |
| **Passive Intel** | Wayback Machine, SecurityTrails | Historical data, DNS records |

*"I can't believe you kids built all this in one afternoon!"*

---

## 📊 Output Format (More Structured Than Summer Vacation Plans)

Results save to `./phineas-results/` as timestamped JSON files:

```json
{
  "target": "john.doe@example.com",
  "workflow": "email_intelligence",
  "duration_seconds": 45.2,
  "summary": {
    "total_plugins": 4,
    "successful": 4,
    "failed": 0,
    "highlights": [
      "1 unique email(s) discovered",
      "12 social media profile(s) found",
      "3 data breach(es) identified"
    ]
  },
  "plugins": {
    "holehe": {
      "status": "success",
      "findings": {
        "accounts": ["twitter", "github", "instagram", "linkedin"]
      }
    },
    "haveibeenpwned": {
      "status": "success",
      "findings": {
        "breaches": [
          {
            "name": "LinkedIn",
            "breach_date": "2021-06-22",
            "pwn_count": 700000000
          }
        ]
      }
    }
  }
}
```

---

## 🔧 Advanced Usage (For When You Go Full Ferb)

### Custom Workflows
Create your own in `workflows/`:

```yaml
name: custom_investigation
target_type: email
steps:
  - name: holehe
    timeout: 60
  - name: sherlock
    timeout: 180
  - name: haveibeenpwned
    timeout: 30
```

### Adding New Plugins

1. Create plugin in `plugins/<category>/your_plugin.py`
2. Extend from `PluginBase`, `CommandLinePlugin`, or `APIPlugin`
3. Implement required methods
4. Add to workflow YAML

See `plugins/__init__.py` for base classes.

### Configuration File

Edit `config/phineas.yaml` for:
- Output directory
- Timeouts and retries
- Plugin settings
- Rate limiting
- API keys

---

## Optional: Cronos Integration

*"BEHOLD! THE CRONOS-INATOR!"*

PHINEAS can optionally enrich [Cronos](https://github.com/yourusername/cronos) security scans:

```bash
python phineas.py cronos --client securit360

# Enriches Cronos scans with:
# • Breach intelligence
# • Social media profiles
# • Additional subdomains
# • OSINT context
```

This is **completely optional** - PHINEAS works perfectly standalone!

---

## Ethical Use (Don't Be Doofenshmirtz Evil)

### Good Uses
- Authorized security assessments
- Corporate threat intelligence
- Red team operations (with permission)
- Bug bounty reconnaissance
- Security research
- Personal privacy audits

### ❌ Bad Uses
- Stalking or harassment
- Unauthorized surveillance
- Personal information theft
- Anything illegal
- Being a creep

*"Curse you, Perry the Platypus!" - What Doofenshmirtz says when you use this tool maliciously*

---

## Troubleshooting (When the Invention Doesn't Work)

### Tool Not Found
```bash
# Reinstall specific tool
pip install sherlock-project --force-reinstall
```

### Timeout Errors
Edit `config/phineas.yaml`:
```yaml
timeout: 600  # Increase from 300
```

### Permission Denied
```bash
pip install --user theHarvester
```

### "Module not found"
```bash
pip install -r requirements.txt --force-reinstall
```

### It's Not Working!
*"Aren't you a little young to be debugging Python code?"*
*"Yes. Yes we are."*

1. Check Python version: `python --version` (need 3.9+)
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Run tools manually to test: `sherlock --help`
4. Check config: `python phineas.py keys`

---

## 🤝 Contributing (Join the Backyard Gang)

Want to add a new OSINT tool? Here's how:

1. **Fork the repo**
2. **Create a plugin** in `plugins/<category>/`
3. **Test it** 
4. **Submit a pull request**
5. **Profit** (in internet points)

Plugin template:
```python
from plugins import CommandLinePlugin

class Plugin(CommandLinePlugin):
    def get_command(self):
        return ['your-tool', self.target]
    
    def parse_output(self, stdout, stderr):
        return {'findings': {}}
```

---

## License

MIT License - See [LICENSE](LICENSE)

**Translation:** Do whatever you want, just don't blame us if it doesn't work. And definitely don't use it for evil.

---

## 🎓 FAQ (Frequently Asked Questions, Unlike What Ferb Says)

**Q: Do I need API keys?**
A: Nope! Most tools work great without them. API keys just add extra features.

**Q: Is this legal?**
A: Yes, for authorized security research. Check your local laws and get permission.

**Q: Will this hack Facebook?**
A: No. This is OSINT (public information), not hacking. Also, we're not Doofenshmirtz.

**Q: Can I use this for bug bounties?**
A: Absolutely! That's exactly what it's for.

**Q: Does it work on Windows?**
A: Yes! We even made a .bat file for you.

**Q: What about Mac/Linux?**
A: Yep, works great. Use the .sh installer.

**Q: Can I add my own tools?**
A: Yes! See the Contributing section.

**Q: Why "PHINEAS"?**
A: Because we're building the most ambitious OSINT framework anyone has ever seen. In one afternoon. In our backyard.

---

## Credits

**Inspired by:** Phineas and Ferb - for teaching us that summer vacation + ambition = amazing things

**Built with:**
- Python (the language, not the pet)
- Free OSINT tools (Sherlock, Holehe, theHarvester, Sublist3r, etc.)
- Way too much caffeine
- Zero permission from Candace

**Special thanks to:**
- The OSINT community
- Coffee
- The letter P (for Perry the Platypus)

---

## 🎬 Final Words

*"Ferb, I know what we're gonna find today!"*

PHINEAS is your all-in-one OSINT automation framework. It's free, it's powerful, and it definitely won't disappear by the time Mom gets home.

Now get out there and do some reconnaissance! (Authorized reconnaissance only, please.)

**Built with love for the security research community**

*"Yes. Yes, we are going to find all the OSINT data anyone has ever seen."*

---

*P.S. - Perry the Platypus approved.*

*P.P.S. - Doofenshmirtz Evil Incorporated is not a supported target.*

*P.P.P.S. - "CANDACE! PHINEAS AND FERB ARE DOING OSINT IN THE BACKYARD!"*
