import csv
import os
import asyncio
from playwright.async_api import async_playwright

# FULL LIST OF KEYWORDS FROM YOUR REQUEST
KEYWORDS = [
    "CRM", "Customer Relationship Management", "Citizen Relationship Management",
    "Constituent Management", "Case Management", "Member Management", "Member 360",
    "Client Management System", "Enterprise CRM", "Community Portal", "Self-Service Portal",
    "Digital Services Platform", "Sales Cloud", "Service Cloud", "Experience Cloud",
    "Marketing Cloud", "Data Cloud", "Tableau", "MuleSoft", "Slack", "Agentforce",
    "AI chatbot", "Conversational AI", "Contact Center Modernization", "Omni-Channel",
    "Knowledge Base", "Workflow Automation", "Tribal CRM", "Tribal Member Services",
    "Tribal Enrollment System", "Tribal Case Management", "Tribal Citizen Portal",
    "Tribal Housing Software", "Tribal Social Services Platform", "Tribal ERP modernization",
    "Tribal digital transformation", "Tribal data sovereignty", "Tribal healthcare CRM",
    "Tribal grants management", "Tribal government modernization", "Native American technology services",
    "Housing", "Housing assistance management", "HUD compliance software", "Tenant management",
    "Housing authority CRM", "Waitlist management", "Health & Human Services",
    "Family wellness platform", "Social services case management", "Benefits eligibility",
    "Behavioral health system", "Patient engagement platform", "Enrollment",
    "Enrollment verification", "Genealogy records", "Tribal ID management",
    "Member records modernization", "Courts/Public Safety", "Tribal court case management",
    "Justice system modernization", "Public safety records management", "Gaming",
    "Guest 360", "Loyalty modernization", "Casino marketing automation",
    "Hospitality CRM", "Player engagement platform", "AI modernization", "Generative AI",
    "Digital transformation", "Legacy system replacement", "Cloud migration",
    "Data integration", "Enterprise data platform", "Data warehouse modernization",
    "Customer experience modernization"
]

async def scrape_site(browser, tribe_name, url):
    """Visits a site and checks for keywords."""
    print(f"Checking {tribe_name} at {url}...")
    try:
        # Open a new browser tab for each tribe
        page = await browser.new_page()
        
        # Go to the URL (timeout after 45 seconds)
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        
        # Get all text from the page
        content = await page.content()
        content_lower = content.lower()

        # Check for matches
        matches = [kw for kw in KEYWORDS if kw.lower() in content_lower]
        
        await page.close()
        return {"tribe": tribe_name, "url": url, "matches": matches}
    except Exception as e:
        print(f"Could not scan {tribe_name}: {str(e)}")
        return {"tribe": tribe_name, "url": url, "matches": [], "error": True}

async def main():
    results = []
    
    async with async_playwright() as p:
        # Launch browser (headless mode)
        browser = await p.chromium.launch(headless=True)
        
        # Load your CSV (ensure the header names match exactly: 'Tribe' and 'Procurement Link')
        try:
            with open('tribal_procurement_links.csv', mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                tasks = []
                for row in reader:
                    # Creating tasks to run in semi-parallel
                    tasks.append(scrape_site(browser, row['Tribe'], row['Procurement Link']))
                
                # Run all scraping tasks
                raw_results = await asyncio.gather(*tasks)
                
                # Filter for only those with hits
                for res in raw_results:
                    if res.get("matches"):
                        results.append(res)
        except FileNotFoundError:
            print("Error: tribal_procurement_links.csv not found in repository.")
            return

        await browser.close()

    # FINAL OUTPUT
    if results:
        print("\n--- DAILY OPPORTUNITY ALERT ---")
        for r in results:
            print(f"TRIBE: {r['tribe']}")
            print(f"LINK: {r['url']}")
            print(f"FOUND: {', '.join(r['matches'])}")
            print("-" * 30)
    else:
        print("No matches found today.")

if __name__ == "__main__":
    asyncio.run(main())
