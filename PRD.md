PRD: ResQNet AI

Version: 0.1 | Context: College fest / hackathon, team of 2

1. Problem

During disasters, centralized apps crash and cellular networks go down. SOS messages arrive scattered (WhatsApp, in-app, texts), unstructured, and in multiple languages. Coordinators have no single view of what is needed, where, and how much, and no efficient way to route rescue teams.

2. Target User
Primary: Rescue coordinators (NDRF / NGOs / control rooms)
Secondary (data source, not designed for in MVP): Affected citizens who send SOS signals
3. Goals and Success Metrics
Metric	Target
SOS extraction precision / recall	TBD (measure a baseline first, then set a target)
End-to-end latency (SOS received → visible on map)	TBD

No numeric targets were provided, so none are invented here. See Open Questions.

4. Core Features
SOS Ingestion: WhatsApp bot (opt-in forwarding) + in-app SOS
NLP Extraction: Extract location, need type, and people count from Hinglish (Roman script), Hindi, and English text; filter spam
Human Verification Queue: Coordinators verify or reject each SOS
Coordinator Dashboard: Map of verified needs and available resources
Graph-based Routing: Model the city as a graph; GNN-based routing; re-route on live road-blockage updates
Basic Risk Map / Forecast: The “predictive” component, kept basic
BLE Mesh SDK (Android): Share SOS with nearby devices offline; sync to cloud once any node gets connectivity
5. User Stories

Coordinator

As a coordinator, I want all SOS requests on one map so I can prioritize response.
As a coordinator, I want to reject fake or spam SOS requests so resources aren’t wasted.
As a coordinator, I want a suggested route for each rescue team that updates when a road gets blocked.
As a coordinator, I want to see a risk map so I can pre-position resources.

Citizen (data source)

As a citizen, I want to send an SOS via WhatsApp or the app in Hindi, Hinglish, or English.
As a citizen, I want my SOS to reach nearby phones and sync later if there is no network.
6. Requirements

Functional

FR1: The WhatsApp bot receives opt-in forwarded messages
FR2: In-app SOS submission (text + location)
FR3: NLP pipeline handles Hinglish, Hindi, and English and outputs structured fields
FR4: Every extracted SOS enters the verification queue; only verified SOS appear on the map
FR5: Routing engine runs on the city graph using a GNN
FR6: Re-route on road-blockage updates
FR7: Basic risk map / forecast
FR8: Android SDK broadcasts and relays SOS over BLE, and syncs to cloud when connectivity returns

Non-functional

Latency and extraction accuracy are measured against the metrics in Section 3
Mesh demo scale: 2-5 phones

Data

NLP training/evaluation: public crisis datasets + synthetic data
Road and resource data: simulated/synthetic (for demo)
7. Edge Cases
Fake, duplicate, or spam SOS (handled via the verification queue)
Multiple SOS reports for the same incident (dedup/merge)
Mixed-script messages and spelling variants (e.g., “paani bhar gaya hai near sector 5”)
Missing or ambiguous location
Intermittent connectivity causing partial mesh sync
Same SOS arriving via both mesh and cloud (duplicate sync)
A road blockage making a destination unreachable
8. MVP Scope

In: WhatsApp bot + in-app SOS, NLP extraction (3 language styles), verification queue, coordinator dashboard, GNN routing on a synthetic graph, basic risk map, Android BLE mesh demo (2-5 phones)

Out: iOS, real-scale mesh, X/Twitter scraping, real government or live feeds, polished citizen-facing app

9. Risks (honest assessment)
Scope is large for 2 people. There are three independent systems: NLP, routing + GNN + risk map, and BLE mesh. The timeline is still unknown, which makes this the biggest risk.
GNN is not required for routing. You chose it as must-have, so it’s included. Give it a clear task (e.g., predict edge travel time or blockage, then run Dijkstra/GA on top), or evaluators will ask why it’s there. It can also feed the risk map.
Accuracy on synthetic data does not reflect real-world accuracy. State this clearly in the demo.
WhatsApp bot needs Business API setup and approval, so check the lead time.