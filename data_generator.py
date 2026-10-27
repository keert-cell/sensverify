"""
Dataset Generator for Fake News Detector
Generates high-quality, realistic Fake.csv and True.csv benchmark datasets
matching the schema of the Kaggle Fake and Real News Dataset (title, text, subject, date).
"""

import os
import random
import pandas as pd

def build_datasets(output_dir="data", count_per_class=250):
    os.makedirs(output_dir, exist_ok=True)
    fake_path = os.path.join(output_dir, "Fake.csv")
    true_path = os.path.join(output_dir, "True.csv")
    
    # Real news templates and components
    real_subjects = ["politicsNews", "worldnews", "scienceNews", "healthNews", "economyNews"]
    
    real_topics = [
        {
            "title": "Senate Approves Bipartisan Infrastructure Investment and Jobs Act in Historic Vote",
            "subject": "politicsNews",
            "date": "August 10, 2021",
            "text": "WASHINGTON (Reuters) - The United States Senate passed a bipartisan $1 trillion infrastructure package on Tuesday, culminating months of negotiations between the White House and lawmakers. The legislation provides major funding for roads, bridges, public transit, clean drinking water networks, and high-speed broadband expansion across rural communities. Voting 69-30, the measure received substantial support from both political parties, sending the landmark bill to the House of Representatives for final consideration. Congressional budget analysts noted the investments represent the largest federal upgrade to public infrastructure in over a generation."
        },
        {
            "title": "NASA James Webb Space Telescope Detects Carbon Dioxide in Exoplanet Atmosphere",
            "subject": "scienceNews",
            "date": "August 25, 2022",
            "text": "CAPE CANAVERAL (Reuters) - NASA's James Webb Space Telescope has captured definitive evidence for carbon dioxide in the atmosphere of a gas giant planet orbiting a sun-like star 700 light-years away. The discovery, accepted for publication in Nature, marks the first time CO2 has been identified on a world outside our solar system. The exoplanet, designated WASP-39b, was observed during transit using Webb's Near-Infrared Spectrograph. Researchers confirmed the spectral signatures reflect high-precision photometric measurements, advancing understanding of planetary formation and evolutionary dynamics."
        },
        {
            "title": "World Health Organization Approves First Malaria Vaccine for Children in High-Transmission Areas",
            "subject": "healthNews",
            "date": "October 6, 2021",
            "text": "GENEVA (Reuters) - The World Health Organization recommended the widespread deployment of the RTS,S/AS01 malaria vaccine among children in sub-Saharan Africa. WHO Director-General Tedros Adhanom Ghebreyesus announced the historic public health breakthrough following successful pilot immunization programs in Ghana, Kenya, and Malawi. Clinical trial data spanning over 2.3 million doses demonstrated a significant 30% reduction in deadly severe malaria episodes when administered alongside standard bed net protection."
        },
        {
            "title": "Federal Reserve Raises Benchmark Interest Rate to Curb Inflationary Pressures",
            "subject": "economyNews",
            "date": "June 15, 2022",
            "text": "WASHINGTON (Reuters) - The Federal Reserve lifted its benchmark overnight interest rate by 75 basis points on Wednesday, the central bank's largest single rate hike since 1994, as policymakers intensified efforts to bring 40-year-high inflation back down toward the target rate of 2%. Chairman Jerome Powell emphasized that stabilizing prices remains essential for sustaining strong employment conditions. Financial markets responded with moderate gains as committee forecasts signaled measured tightening over forthcoming monetary policy cycles."
        },
        {
            "title": "European Union Reaches Climate Pact Mandating 55% Emission Reduction by 2030",
            "subject": "worldnews",
            "date": "April 21, 2021",
            "text": "BRUSSELS (Reuters) - European Union member states and the European Parliament finalized a legally binding climate agreement on Wednesday to reduce net greenhouse gas emissions by at least 55% by 2030 compared to 1990 levels. Negotiators concluded talks after overnight sessions in Brussels, anchoring the European Green Deal into statutory law. Environment ministers stated that regulatory benchmarks will accelerate renewable energy adoption, modernize electric grids, and phase out fossil fuel subsidies across member economies."
        },
        {
            "title": "Global Semiconductor Alliance Announces Joint Research Initiative on 2nm Architecture",
            "subject": "scienceNews",
            "date": "November 14, 2022",
            "text": "TOKYO (Reuters) - Major technology leaders and research institutes across Japan, Europe, and North America announced a cooperative research initiative to accelerate commercial manufacturing of next-generation 2-nanometer semiconductor chips. The consortium focuses on gate-all-around (GAA) transistor designs and extreme ultraviolet (EUV) lithography systems. Government officials pledged financial incentives to bolster supply chain resilience and support domestic wafer fabrication capacities."
        },
        {
            "title": "United Nations Climate Conference Finalizes Loss and Damage Fund Agreement",
            "subject": "worldnews",
            "date": "November 20, 2022",
            "text": "SHARM EL-SHEIKH (Reuters) - Envoys at the COP27 climate summit agreed to establish a dedicated fund to assist developing nations vulnerable to climate disasters. The breakthrough deal followed extensive negotiations over financial mechanisms and operational oversight. Representatives from island states praised the decision as a decisive recognition of climate equity, while international bodies began drafting transitional committee guidelines for institutional disbursements."
        },
        {
            "title": "Treasury Department Reports Expansion in Renewable Energy Jobs Across Manufacturing Sector",
            "subject": "economyNews",
            "date": "March 18, 2023",
            "text": "WASHINGTON (Reuters) - Clean energy manufacturing investments stimulated private sector job growth across multiple states during the past fiscal year, according to a report released by the U.S. Department of the Treasury. Employment in solar photovoltaic assembly, domestic battery storage manufacturing, and wind turbine installations rose by 8.4%. Economists noted that regional supply chain localization helped mitigate freight bottlenecks and created long-term technical employment opportunities."
        }
    ]
    
    # Fake news templates and components
    fake_subjects = ["News", "politics", "conspiracy", "rumors", "clickbait"]
    
    fake_topics = [
        {
            "title": "SHOCKING BOMBSHELL: Whistleblower Exposes Secret Government Mind Control Chips in Public Drinking Water!",
            "subject": "conspiracy",
            "date": "August 12, 2021",
            "text": "You will not believe what corrupt officials have been hiding from the public! An anonymous insider has just leaked explosive classified documents proving that the federal government is injecting microscopic nano-chips into municipal drinking water systems across the nation. Mainstream media refuses to report this terrifying truth! The microchips are supposedly activated by 5G cell towers to alter voter behavior during elections. Millions of patriotic citizens are waking up to this wicked globalist agenda. Share this urgently before the deep state scrubs it from the internet!"
        },
        {
            "title": "BREAKING: NASA Caught Faking Mars Rover Landing on Secret Hollywood Soundstage!",
            "subject": "conspiracy",
            "date": "September 3, 2022",
            "text": "PROOF IS FINALLY HERE! Astonishing leaked camera footage reveals that NASA never sent rovers to Mars. Instead, high-ranking directors staged the entire Martian surface inside an abandoned warehouse in the Nevada desert. Stage lighting reflections and stagehands holding props are clearly visible in raw unedited frames! The government has stolen trillions in taxpayer money while fabricating outer space accomplishments. The global elites are trembling as the veil of deception collapses. Share this article immediately!"
        },
        {
            "title": "MIRACLE CURE: Doctors Terrified After Backyard Weed Cures 100% of Terminal Diseases in 24 Hours!",
            "subject": "clickbait",
            "date": "October 14, 2021",
            "text": "Big Pharma is furious and trying to silence this courageous local healer! A simple garden plant that grows freely in your backyard has been proven to cure every single terminal disease overnight with zero side effects. Greedy pharmaceutical executives held emergency closed-door meetings to ban this miraculous remedy because it would eliminate their trillion-dollar profits permanently. Thousands of patients have already canceled expensive prescriptions. Watch this banned secret video before corrupt judges take it down!"
        },
        {
            "title": "UNBELIEVABLE: Secret Underground Bunker Discovered Beneath White House With Billions in Stolen Gold!",
            "subject": "politics",
            "date": "July 19, 2022",
            "text": "A shocking expose has just rocked Washington insiders! Elite construction workers blew the whistle on a subterranean labyrinth constructed beneath the capital containing pallets of unrecorded gold bullion and classified extraterrestrial treaties. Corrupt politicians were caught attempting to smuggle the riches offshore before upcoming audits. The deep state is scrambling for cover as federal marshals prepare massive arrest warrants. Do not trust what television news anchors tell you, the truth is out!"
        },
        {
            "title": "WATCH: Leaked Video Shows Hologram Glitch in Sky Proves Earth is Enclosed Under Giant Glass Dome!",
            "subject": "conspiracy",
            "date": "May 4, 2022",
            "text": "The greatest conspiracy in human history has just been exposed for the whole world to see! Thousands of witnesses recorded a massive optical glitch during a thunderstorm that caused the artificial sky projection to freeze for 45 seconds, revealing a gigantic reinforced glass ceiling. Elite scientists and puppet governments have lied to humanity for centuries to keep us trapped. Spread this truth far and wide before Big Tech censors delete all digital evidence!"
        },
        {
            "title": "SCANDAL: Secret Globalist Cabal Announces Plan to Replace Human Currency with Mandatory Fingerprint Scans Next Week!",
            "subject": "News",
            "date": "February 8, 2023",
            "text": "They are not even hiding their evil tyranny anymore! Anonymous sources within global banking cartels confirmed that all paper money and bank accounts will be seized without warning next Tuesday. Citizens will be denied access to food and fuel unless they submit to biometric chip implants. Spread the word now to prepare your family before the total collapse of personal liberty. The mainstream media won't say a single word because they are bought and paid for!"
        },
        {
            "title": "ALERT: Secret Weather Machine Unleashed to Deliberately Trigger Winter Freezes Across the Nation!",
            "subject": "rumors",
            "date": "January 11, 2023",
            "text": "Scientists have confirmed our worst fears! High-ranking shadow directors activated high-frequency atmospheric transmitters to manipulate jet stream currents and plunge millions into freezing chaos. The purpose? To artificially hike energy utility prices and make corrupt billionaires even richer! Leaked satellite imagery clearly shows unnatural circular wave formations pulsing across the cloud cover. Demand answers from your politicians immediately before they strike again!"
        },
        {
            "title": "EXPOSED: Secret Deep State Election Computer Reset Overrides All Ballots in Midnight Raid!",
            "subject": "politics",
            "date": "November 9, 2022",
            "text": "The stolen election coverup is completely unraveling! High-tech forensic auditors caught rogue foreign servers modifying voting machine algorithms at 3:14 AM. Millions of legal votes vanished into thin air while phantom votes were inserted into database clusters. Corrupt officials refused to hand over server logs, but patriotic hackers recovered the raw data. Share this viral bombshell before the corrupt establishment deletes the backup files!"
        }
    ]

    # Generate diverse real articles
    real_data = []
    real_entities = [
        ("Federal Reserve", "Jerome Powell", "monetary policy committee", "interest rate benchmarks", "inflation metrics"),
        ("European Space Agency", "Director Josef Aschbacher", "Ariane 6 launch team", "Earth observation telemetry", "spectroscopic sensors"),
        ("United Nations Environment Programme", "Inger Andersen", "multilateral environmental panel", "biodiversity preservation treaty", "sustainable resource standards"),
        ("World Meteorological Organization", "Celeste Saulo", "climate forecasting institute", "global ocean temperature monitoring", "meteorological telemetry"),
        ("Department of Energy", "Secretary Jennifer Granholm", "national renewable energy laboratory", "clean grid modernization initiative", "battery manufacturing grants"),
        ("National Institutes of Health", "Dr. Monica Bertagnolli", "clinical research collaborative", "phase III clinical trials", "peer-reviewed medical outcomes"),
        ("Bank of England", "Governor Andrew Bailey", "monetary policy board", "gilt yield stabilization", "macroeconomic financial reports"),
        ("International Energy Agency", "Fatih Birol", "global energy transition council", "offshore wind deployment", "photovoltaic capacity growth")
    ]
    
    real_actions = [
        "published comprehensive peer-reviewed findings regarding",
        "announced official bilateral regulatory standards to address",
        "allocated targeted federal grants to support research in",
        "ratified international guidelines aimed at standardizing",
        "concluded multi-stage clinical validation trials evaluating",
        "released quarterly statistical indicators demonstrating progress in",
        "convened an intergovernmental symposium to coordinate",
        "unveiled verified engineering benchmarks designed for"
    ]
    
    for i in range(count_per_class):
        base = random.choice(real_topics)
        entity = random.choice(real_entities)
        action = random.choice(real_actions)
        
        title = f"{entity[0]} {action.capitalize()} {entity[3].title()} in Official Report"
        text = (
            f"WASHINGTON (Reuters) - The {entity[0]} formally {action} {entity[3]} during a joint briefing on {base['date']}. "
            f"Speaking on behalf of the {entity[2]}, {entity[1]} outlined rigorous empirical data and verifiable benchmarks. "
            f"According to published documentation, the initiative established measurable milestones for {entity[4]} "
            f"following extensive collaboration with accredited scientific and regulatory institutions. "
            f"Independent analysts praised the transparent methodology and confirmed that data audits aligned with statutory standards. "
            f"Further implementation schedules will be finalized during the upcoming international session."
        )
        real_data.append({
            "title": title,
            "text": text,
            "subject": random.choice(real_subjects),
            "date": base["date"]
        })

    # Generate diverse fake articles
    fake_data = []
    fake_buzzwords = [
        "BOMBSHELL REVEALED", "SHOCKING EXPOSE", "MAINSTREAM MEDIA SILENT", "DEEP STATE PANICS",
        "LEAKED FOOTAGE", "TERRIFYING TRUTH", "WHAT THEY ARE HIDING", "WHISTLEBLOWER TESTIFIES",
        "THEY DON'T WANT YOU TO KNOW", "MUST WATCH VIDEO", "CONSPIRACY CONFIRMED"
    ]
    
    fake_claims = [
        ("secret nanotechnology microchips", "implanted in public drinking water", "5G satellite towers", "brainwash patriotic citizens"),
        ("miracle herbal extract", "eradicates all chronic illnesses in 48 hours", "corrupt Big Pharma bosses", "burn medical patents"),
        ("underground cavern filled with alien technology", "discovered under capital building", "shadow government elites", "control world stock markets"),
        ("weather manipulation death rays", "triggered unprecedented tornadoes across farmland", "globalist bankers", "force people into smart cities"),
        ("fake holographic planetary moon", "projected by high altitude stealth blimps", "clandestine scientific societies", "conceal cosmic energy waves"),
        ("covert midnight election database hack", "reassigned millions of legal votes", "corrupt partisan officials", "destroy democratic transparency")
    ]
    
    for i in range(count_per_class):
        base = random.choice(fake_topics)
        claim = random.choice(fake_claims)
        buzz = random.choice(fake_buzzwords)
        
        title = f"{buzz}: {claim[0].upper()} {claim[1].upper()}!"
        text = (
            f"You won't hear this anywhere on the television news! An anonymous insider has just leaked classified evidence "
            f"revealing that {claim[0]} are being {claim[1]} to {claim[3]}. "
            f"The corrupt {claim[2]} held emergency secret meetings to censor all independent journalists trying to expose this wicked agenda. "
            f"Do not trust the official coverup! Millions of truth-seekers are sounding the alarm before corrupt authorities scrub all records. "
            f"Share this viral bombshell with everyone you know before Big Tech bans this website forever!"
        )
        fake_data.append({
            "title": title,
            "text": text,
            "subject": random.choice(fake_subjects),
            "date": base["date"]
        })
        
    df_real = pd.DataFrame(real_data)
    df_fake = pd.DataFrame(fake_data)
    
    df_real.to_csv(true_path, index=False)
    df_fake.to_csv(fake_path, index=False)
    print(f"Generated {len(df_real)} Real news rows to {true_path}")
    print(f"Generated {len(df_fake)} Fake news rows to {fake_path}")

if __name__ == "__main__":
    build_datasets()
