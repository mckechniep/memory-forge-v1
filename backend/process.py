import sys
import re
import json
import os
from pathlib import Path
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Exit if API key is not set
if not openai.api_key:
    print("OPENAI_API_KEY not set. Please export it.")
    sys.exit(1)

# --- Tagging Logic for RAG ---
# This function analyzes text and suggests relevant tags based on keyword matching
# Input: text (string) to analyze, top_n (int) number of tags to return
# Output: list of the most relevant tags (strings)
def suggest_tags(text, top_n=5):
    # Dictionary mapping tag categories to related keywords
    regex_tag_patterns = {
    "meta": [
        r"\b(llm|ai|model|neural|trained|parameters|rag)\b",
        r"\b(digital[- ]?twin|memory[- ]?bank|what i am|self[- ]?aware|fine[- ]?tuned)\b",
        r"\bavatar\b",
        r"\b(large[- ]?language[- ]?model)\b",
        r"\b(generative|retrieval[- ]?augmented)\b",
        r"\b(supervised\s+)?fine[- ]?(?:tune|tuning|tuned)\b"
    ],
    
    "childhood": [
        r"\b(child(ren|hood|ish)?|formative(?: years)?|little(?: one(s)?)?|kid(s)?|infant(ile)?|infancy|bab(y|ies)|newborn|born|birth|toddler)\b",
        r"\b(grow(ing)? up|grew up|raised)\b",
        r"\b(daycare|preschool(er)?|pre-kindergarten|kindergarten(er)?|k1|k-one|k2|k-two)\b",
        r"\b(elementary school|primary school|lower school|grade school)\b",
        r"\b(first|second|third|fourth|fifth|sixth|seventh|eighth) grade\b",
        r"\b(1st|2nd|3rd|4th|5th|6th|7th|8th) grade\b",
        r"\b(arts and crafts|babysit(ter|ting)?|nanny|recess)\b",
        r"\b(playdate(s)?|playgroup|playmate|playground|playdate)\b",
        r"\bschool(yard)?\b"
    ],
    
    "adolescence": [
        r"\b(adolescen(ce|t)|teenage(r)?|teen(s)?|youngster|youth|younger)\b",
        r"\b(grasshopper|padawan)\b",
        r"\b(high(?:[- ]?school)|middle[- ]?school|secondary school|asl|american school(?: in london)?)\b",
        r"\b(ninth|tenth|eleventh|twelfth) grade\b",
        r"\b(the arcade|the shop)\b"
    ],
    
    "adulthood": [
        r"\b(adulthood|adult(ing)?|twenties|thirties|young man|grown man|grownup)\b",
        r"\b(responsibilities|career|job|work|office|boss|promotion)\b"    
    ],
    
    "family": [
        r"\b(famil(y|ies)|relatives|blood|clan|lineage)\b",
        r"\b(parent(s)?|mom|dad|sibling|brother|sister)\b",
        r"\b(alec|caleb|kyle|deirdre|dee|colin|meaul)\b",
        r"\b(aunt(s)?|uncle(s)?|cousin(s)?)\b",
        r"\b(uncle malcolm|uncle bill|uncle john|aunt lorna|aunt carol|aunt joanne|aunt maryanne|uncle kevin|aunt jane)\b",
        r"\b(ancest(ry|or|ors))\b",
        r"\b(grandparent(s)?|grandma|grandmother|gran|granny|grandpa|grandfather)\b",
        r"\b(in-laws|spouse|partner|husband|wife)\b"
    ],
    
    "identity": [
        r"\b(identity|self|myself|ego|me)\b",
        r"\b(i am|alias|nickname)\b",
        r"\b(how i describe|personality|who i am|inner self|core self)\b"
    ],
    
    "emotion": [
        r"\b(happ(y|ier|iest|iness)|joy(ful|ous)?|excited|hype|elat(ed|ion)|ecsta(tic|sy)|thrilled|delighted|pleased|glad)\b",
        r"\b(sad(ness|dened)?|angry|mad|frustrated|upset|depress(ed|ing|ion)?|melanchol(y|ic)|down|blue|gloomy|despondent)\b",
        r"\b(scared|fear(ful)?|anxious|nervous|worry|worried|panic(ked|king)?|dread(ed|ing)?|afraid|fearful|terrified)\b",
        r"\b(guilt(y)?|ashamed|shame(d|ful)?|proud|pride|regret(ful|ted)?|remorse(ful)?|embarrass(ed|ing|ment)|mortif(ied|ying))\b",
        r"\b(love(d|s)?|heartbroken|lonely|euphoria|nostalgic|adore(d|s)?|cherish(ed)?|fond of|attachment|affection(ate)?)\b",
        r"\b(grief|panic|relief|emotion(al|ally)?|overwhelmed|feeling(s)?|felt|feel(ing)?)\b",
        r"\b(meltdown|breakdown|tears|cry(ing|ies|ed)?|laughed|laugh|sob(bing|bed)?|tear(s|ful|y)?)\b",
        r"\b(anger|angrier|angriest|furious|irate|outraged|rage|enraged)\b",
        r"\b(exhaust(ed|ing)|stress(ed|ful)|burn(t|ed) out)\b",
        r"\b(hate(d|s)?|detest(ed)?|loathe(d)?|despise(d)?|resent(ed|ment)?|contempt|disdain)\b",
        r"\b(accomplish(ed|ment)|satisf(ied|action)|content(ed|ment)?)\b",
        r"\b(frustrat(ed|ing)|annoy(ed|ing)|irritat(ed|ing))\b"
    ],
    
    "memory": [
        r"\bremember\b",
        r"\bi remember\b",
        r"\b(flashback|memory|memories|memor(y|ies|able|ial))\b",
        r"\b(can still see|can't forget|etched|stuck with me|imprinted|burned into|seared into|lodged in|imprinted on)\b",
        r"\b(won't ever forget|came back to me|triggered|recall(ing)?|recollect(ion)?|reminisce)\b",
        r"\b(thought about|vivid(ly)?|nostalgia|nostalgic|felt like yesterday)\b",
        r"\b(brought|comes|came) (back|to mind|flooding back)\b",
        r"\b(never|won't|will never|can't|cannot|can never) forget\b",
        r"\b(still see|still hear|still feel|still remember|still recall)\b",
        r"\b(back then|those days|that time|that day|that moment|when I was)\b"
    ],
    
    "belief": [
        r"\b(belief|believe|ideology)\b",
        r"\b(i think|i know|knowledge|core beliefs)\b",
        r"\bi (believe|think|know|feel|suppose|suspect|assume|reckon|guess|figure|maintain|hold that|am convinced|am certain)\b",
        r"\b(in my (opinion|view|estimation|mind|judgment|understanding))\b",
        r"\b(from my (perspective|standpoint|point of view))\b",
        r"\bmy (belief|thought|position|stance) is\b"
    ],
    
    "relationships": [
        r"\b(relationship|friend|best friend|partner|ex)\b",
        r"\b(girlfriend|boyfriend|romance|fling|situationship|crush)\b",
        r"\b(intimacy|love|chemistry|connection|bond)\b",
        r"\b(jealousy|trust|breakup|falling in love)\b",
        r"\b(heart|together|apart|attraction)\b"
    ],
    
    "reflection": [
        r"\b(looking back|in hindsight|it hit me)\b",
        r"\b(i realized|i've been thinking|i used to think|it occurred to me)\b",
        r"\b(i learned|i noticed|what i saw|looking inward)\b",
        r"\b(self-awareness|reflection|reflect(ing)?)\b",
        r"\b(growth|change in me|insight|clarity)\b",
        r"\bi (realized|discovered|learned|noticed|found out|came to understand|see now)\b",
        r"\bit (hit|struck|occurred to|dawned on) me\b",
        r"\b(reflecting|reflecting on|in retrospect|upon reflection|thinking about it)\b",
        r"\bafter (considering|thinking about|pondering|contemplating)\b"
    ],
    
    "humor": [
        r"\b(funny|hilarious|lol|joke(d|s|r)?|banter|jest(ing)?|kidding|amusing|comedy|comedic|humor(ous)?)\b",
        r"\b(roasted|laughed|laugh(ed|ing|ter)?|clown|absurd|ridiculous|chuckle(d)?|giggle(d)?|snicker(ed)?|guffaw(ed)?)\b",
        r"\b(sarcastic|sarcas(m|tic)|dark humor|meme|ironic|irony|prank(ed)?|facetious|tongue.in.cheek)\b",
        r"\b(goofy|got jokes|stupid funny|dry humor|one-liner|witty|clever|quip|pun)\b",
        r"\b(tease(d|s)?|mock(ed|ing|ery)?|ridicul(e|ous|ed))\b",
        r"\b(roll(ed|ing)? (my|your|his|her|their) eyes)\b",
        r"\b(lol(ol)*|lool|lmao(o+)?|lmfao|a?ha(ha)+)\b",
    ],
    
    "dream": [
        r"\b(dream(ed|s|ing)?|nightmare|lucid)\b",
        r"\b(surreal|vision|dreamlike|fantasy|symbolic)\b",
        r"\b(woke up|sleep|asleep|subconscious)\b",
        r"\b(unreal|hallucinated|imagination|otherworldly|trippy)\b"
    ],
    
    "goal": [
        r"\b(goal|ambition|objective|vision|future)\b",
        r"\b(i want to|i hope|i'm working on|bucket list)\b",
        r"\b(i'm aiming for|my dream|milestone|target)\b",
        r"\b(next step|plan|roadmap)\b"
    ],
    
    "inspiration": [
        r"\b(inspired|inspiration|role model|hero|idol)\b",
        r"\b(motivation|spark|ignite|reminded me|what pushes me)\b",
        r"\b(light a fire|fuel|admire|who i look up to|legend|powerful)\b"
    ],
    
    "education": [
        r"\b(school|education|class|learning|teacher)\b",
        r"\b(preschool|middleschool|highschool|college|uni|university)\b",
        r"\bimmersion\b"
    ],
    
    "military": [
        r"\b(army|infantry|marine|air force|military)\b",
        r"\b(unit|fire(team|fight)|platoon|squad|base|ops)\b",
        r"\b(mission|combat|war|PT|training|field problem|west[- ]?point|cadet(s)?)\b",
        r"\b(deploy(ed|ment|ing)?|tour|enlist(ed|ment)?|oath|service)\b",
        r"\b(sergeant|rank|corporal)\b",
        r"\b(qrf|special forces|delta|3[- ]?15)\b"
    ],
    
    "career": [
        r"\b(career|job|work|boss|co-worker)\b",
        r"\b(hired|fired|promotion|quit|resume|interview)\b",
        r"\b(position|title|grind|corporate|nine to five)\b",
        r"\b(dream job|intern|freelance|ambition|hustle)\b",
        r"\b(project|team|startup|clients)\b"
    ],
    
    "mental_health": [
        r"\b(burnout|anxiety|depression|mental health)\b",
        r"\b(breakdown|healing|therapy|struggling)\b",
        r"\b(stressed|panic|coping|trauma|triggered)\b",
        r"\b(overwhelmed|isolation|sleep disorder)\b",
        r"\b(self-care|resilience|inner work|mindset)\b",
        r"\b(addiction|ADHD|bi[- ]?polar|PTSD)\b"
    ],
    
    "biography": [
        r"\b(born|raised|childhood|background|life)\b"
    ],
    
    "life_event": [
        r"\b(born|moved|lived|raised|birthday|war)\b",
        r"\b(graduated|started|ended|quit|got hired|fired)\b",
        r"\b(broke up|divorced|married|death|joined)\b",
        r"\b(enlisted|deployed|return|trip|transition)\b",
        r"\b(turning point|milestone|incarcerated|sentenced)\b",
        r"\b(rehab|came home)\b"
    ],
    
    "location": [
        r"\b(london|england|america|summit|uk)\b",
        r"\b(new jersey|new york city|arizona|spain)\b"
    ],
    
    "grateful": [
        r"\b(grateful|thankful|fortunate|blessed)\b"
    ],
    
    "privileged": [
        r"\b(privileged|wealth|affluent|elite|rich|upperclass|wealthy)\b"
    ],
    
    "travel": [
        r"\b(travel(ling)?|trip|vacation|visit|explore)\b"
    ],
    
    "god": [
        r"\b(god|gods|creator|creation|higher power|universal spirit)\b",
        r"\b(omnipotent|deity|religion|religious|faith)\b",
        r"\b(catholic|catholicism|spirit|spiritual|spirituality)\b",
        r"\b(white light|alcoholics anonymous|twelve step)\b",
        r"\b(lord|holy spirit|jesus|king of kings)\b",
        r"\b(pray(er|ing)?|amen|worship|eternal|heaven|supreme being)\b"
    ],
    
    "society": [
        r"\b(societ(y|ies|al)|social|sociology)\b",
        r"\b(democracy|democratic|western|civilized society)\b",
        r"\b(egalitarianism|politics|political|military|political power)\b",
        r"\b(elites|capitalism|collective|law|institutions)\b",
        r"\b(government|citizen|economy|americans|people|other people)\b",
        r"\b(individual|individualism|norms)\b"
    ],
    
    "culture": [
        r"\b(culture|cultural|multicultural|multiculturalism|globalism)\b",
        r"\b(upbringing|race|racial|community|region)\b",
        r"\b(traditions|traditional|religion|beliefs|background)\b",
        r"\b(history|values|country|nationality)\b",
        r"\b(celtic|irish|scottish|ethnicity|ethnic|identity)\b",
        r"\b(ritual|music|art|heritage|roots)\b"
    ],
    
    "question": [
        r"\bwhat (do i think|if)\b",
        r"\bhow come\b",
        r"\?\B",
        r"\b(what|why|how|when|where|who) (if|do|did|does|should|would|could|is|are|was|were)\b",
        r"\?+", 
        r"\bwonder(ing|ed)? (if|about|why|how|what)\b"
    ],
    
    "hobbies": [
        r"\b(hobby|hobbies|pastime|leisure|recreational|for fun)\b",
        r"\b(enjoy|love|like) (to|doing)\b",
        r"\bin my (free|spare) time\b",
        r"\b(weekend|evenings|after work|off time) I (usually|often|sometimes|typically|always)\b",
        r"\bi (collect|play|practice|build|create|make|craft|draw|paint|write|read|watch|listen to|go|workout)\b",
        r"\b(gaming|reading|writing|hiking|biking|swimming|running|jogging|cooking|baking|gardening|crafting|photography|painting|drawing|singing|dancing|collecting|traveling|camping|fishing|hunting|knitting|sewing|woodworking|programming|coding)\b"
    ],
    
    "skills": [
        r"\b(skill|skills|ability|abilities|talent|talents|expertise|proficiency|competency|competent|capable|adept)\b",
        r"\bi('m| am) (good|great|excellent|proficient|skilled|talented|expert) at\b",
        r"\bi can (speak|code|program|write|design|build|create|analyze|solve|fix|troubleshoot|organize|manage|lead|teach|train|communicate|negotiate)\b",
        r"\b(learned|taught myself|studied|practiced|mastered|developed|acquired|honed)\b",
        r"\b(fluent|intermediate|advanced|beginner|novice|professional) (level|proficiency)\b",
        r"\b(years of experience|background in|trained in|certified in|degree in|qualified in)\b",
        r"\b(technical|soft|hard|analytical|creative|management|leadership|interpersonal|communication|problem.solving) skills\b"
    ],
    
    "media": [
        r"\b(book|books|novel|novels|audiobook|audiobooks|story|stories|fiction|non-fiction|memoir|biography|literature)\b",
        r"\b(movie|movies|film|films|documentary|documentaries|series|show|shows|program|programs|episode|episodes)\b",
        r"\b(music|song|songs|album|albums|artist|artists|band|bands|musician|musicians|concert|concerts|playlist|playlists)\b",
        r"\b(game|games|gaming|video game|video games|played|playthrough|campaign|multiplayer|single-player)\b",
        r"\b(watched|read|listened to|binged|streamed|playing|played|reading|watching|listening)\b",
        r"\b(favorite|favourites|prefer|love|enjoy|recommend|fan of|obsessed with|addicted to)\b",
        r"\b(netflix|hulu|spotify|youtube|amazon|apple|disney|hbo|showtime|peacock|paramount|twitch)\b",
        r"\b(genre|type|category|style|similar to|like|reminds me of)\b",
        r"\b(podcast|stream|channel|platform|subscription|streaming service)\b"
    ],
    
    "preferences": [
        r"\b(prefer|preference|preferable|preferably|rather|instead|choice|choose|option|favorite|favourite|best|ideal|optimal|top choice)\b",
        r"\bi (like|love|enjoy|prefer|favor|fancy|adore|appreciate|gravitate toward|am drawn to|tend to choose)\b",
        r"\bi (don't|do not|dislike|hate|can't stand|avoid|detest|loathe) (like|enjoy|prefer)\b",
        r"\b(rather than|as opposed to|in contrast to|over|more than|better than|not as much as)\b",
        r"\b(food|drink|cuisine|restaurant|meal|dish|flavor|taste|texture)\b",
        r"\b(style|fashion|clothing|outfit|dress|wear|aesthetic|design|decor|appearance)\b",
        r"\b(color|colour|shade|hue|tone)\b",
        r"\b(music|movie|book|game|activity|hobby) (preference|type|genre|style)\b",
        r"\b(sweet|salty|spicy|savory|bitter|sour|mild|strong|light|heavy|rich|simple)\b"
    ],
    
    "routine": [
        r"\b(routine|habit|ritual|practice|schedule|regimen|pattern|daily|weekly|monthly|regularly|consistently)\b",
        r"\b(morning|night|evening|afternoon|day|weekend|weekday) routine\b",
        r"\b(every|each) (day|morning|night|evening|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|weekend|week|month)\b",
        r"\b(always|usually|typically|normally|generally|often|regularly|consistently|habitually) (do|does|start|begin|end|finish)\b",
        r"\b(first thing|last thing|before|after) (in the morning|at night|I wake up|I go to bed|breakfast|lunch|dinner|work|exercise)\b",
        r"\b(set|strict|flexible|changing|adjustable|consistent) (schedule|routine|habits|practices)\b",
        r"\b(wake up|get up|rise|sleep|go to bed|eat|shower|exercise|meditate|work|commute|travel)\b"
    ],
    
    "philosophy": [
        r"\b(philosophy|philosophical|belief system|worldview|outlook|perspective|viewpoint|stance|position|mindset)\b",
        r"\b(believe|think|feel|maintain|hold that|consider|value|principle|ethic|moral|virtue)\b",
        r"\bi (believe|think|feel|maintain|hold that) (we should|people should|humanity should|society should|everyone should|no one should)\b",
        r"\b(right|wrong|good|bad|ethical|unethical|moral|immoral|just|unjust|fair|unfair|virtue|vice)\b",
        r"\b(meaning of life|purpose|existence|consciousness|reality|truth|knowledge|wisdom|enlightenment|spiritual|religious)\b",
        r"\b(life (philosophy|principle|value|lesson|teaching))\b",
        r"\b(guide|guides|guided|guiding) (me|my|principle|philosophy|belief|action|decision|choice|life)\b",
        r"\b(stoic|buddhist|existentialist|nihilist|humanist|pragmatist|utilitarian|libertarian|conservative|progressive|liberal|religious)\b"
    ],

    "political": [
        # General politics / government terms
        r"\b(politics|political|politically|government|governance|state|public policy|civil service)\b",
        r"\b(administration|authority|regime|governor|mayor|senator|congressman|congresswoman|representative|president|prime minister)\b",
        
        # Political ideologies / affiliations
        r"\b(democrat(ic)?|republican(s)?|liberal(s)?|conservative(s)?|moderate(s)?|progressive(s)?|left[- ]?wing|right[- ]?wing|centrist)\b",
        r"\b(libertarian(s)?|socialist(s)?|communist(s)?|anarchist(s)?|fascist(s)?|authoritarian|totalitarian)\b",
        
        # Electoral processes
        r"\b(voting|election(s)?|campaign(s)?|ballot|referendum|gerrymander(ing)?|poll(s|ing)?|primary|caucus|electoral college)\b",
        r"\b(vote(d|r)?|campaign(er|ing)?|candidate(s)?|platform|agenda)\b",
        
        # Government institutions
        r"\b(congress|senate|house of representatives|parliament(ary)?|supreme court|judicial|justice|constitutional)\b",
        r"\b(legislation|bill|amendment|constitution|law(maker|making)?)\b",
        
        # Political activities and discourse
        r"\b(lobby(ing|ist)?|filibuster|protest|demonstration|rally|movement|activism|activist)\b",
        r"\b(debate|partisan|bipartisan|across the aisle|gridlock|polarization|division)\b",
        
        # Political power / influence
        r"\b(power structure|political power|elite(s)?|establishment|ruling class|deep state)\b",
        r"\b(political system|ideology|party politics|official(s)?|politician(s)?)\b",
        
        # Global systems and philosophies
        r"\b(socialism|capitalism|communism|democracy|autocracy|dictatorship|oligarchy|monarchy|federalism|theocracy)\b",
        r"\b(nationalist|globalist|populist|isolationist|imperialist|colonialist)\b",
        
        # Policy areas
        r"\b(foreign policy|domestic policy|diplomacy|international relations|reform)\b",
        
        # Personal political expressions
        r"\b(issue|stance|position|view|viewpoint|opinion) on\b",
        r"\bi (voted|support|oppose|believe) (that|in|the)\b",
        r"\bmy (political|stance|position|view|opinion|belief) (is|on|about)\b"
    ],

    "economic": [

        # General economy and finance terms
        r"\b(econom(y|ic|ics)|economist(s)?|fiscal|financial|finance|macro(economics)?|micro(economics)?)\b",
        r"\b(market(s)?|trade|trading|investment(s)?|stock market|inflation|deflation|recession|depression|GDP)\b",

        # Money, income, and class
        r"\b(money|income|wage(s)?|salary|earnings|wealth|rich|poor|poverty|middle class|upper class|working class)\b",
        r"\b(budget(s)?|paycheck|net worth|debt|loan(s)?|credit|interest rate(s)?)\b",

        # Business and employment
        r"\b(job(s)?|employment|unemployment|labor|workforce|hiring|firing|layoff(s)?|gig economy)\b",
        r"\b(business(es)?|company|corporate|corporation|industry|industries|entrepreneur(s)?|startup(s)?)\b",

        # Economic inequality and distribution
        r"\b(inequality|income gap|wealth gap|economic disparity|distribut(ion|e|ing)|redistribution)\b",
        r"\b(capital|capitalist|capitalism|socialism|communism|neoliberal(ism)?|trickle[- ]?down|supply[- ]?side)\b",

        # Government intervention and systems
        r"\b(tax(es|ed)?|subsidy|bailout|welfare|social security|stimulus|minimum wage|basic income)\b",
        r"\b(regulation|deregulation|privatization|public sector|free market|mixed economy|planned economy)\b",

        # International economic terms
        r"\b(global market|international trade|tariff(s)?|import(s)?|export(s)?|exchange rate(s)?|currency|IMF|World Bank|economic sanctions)\b"
    ],

    "time_periods": [
        r"\b(childhood|teenage years|teens|adolescence|young adulthood|adulthood|college years|university days|school days)\b",
        r"\b(when I was (young|a kid|a child|a teenager|in school|in college|in my twenties|in my thirties|in my forties))\b",
        r"\b(elementary school|middle school|high school|college|university|grad school|graduate school)\b",
        r"\b(in the (80s|90s|2000s|2010s|2020s|eighties|nineties|two thousands|twenty tens))\b",
        r"\b(early|mid|late) (childhood|teens|twenties|thirties|forties|fifties|career|life)\b",
        r"\b(age|aged) (of|at) (five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)\b",
        r"\b(during|before|after) (college|university|high school|graduation|marriage|divorce|birth|death|childhood|adolescence|retirement)\b",
        r"\b(years ago|decade ago|long time ago|back then|in those days|at that time|previously|formerly|once)\b",
        r"\b(baby|toddler|kid|child|teen|young adult|adult|middle age|senior)\b"
    ],

    "contexts": [
        r"\b(at|in|during) (work|home|school|college|university|church|gym|office|store|restaurant|library|hospital|party|meeting|conference|interview)\b",
        r"\b(while|when) (working|studying|traveling|driving|flying|walking|running|exercising|shopping|eating|cooking|cleaning|reading|writing|watching|listening)\b",
        r"\b(with|around) (family|friends|colleagues|coworkers|classmates|roommates|neighbors|strangers|boss|manager|teacher|professor|doctor|client|customer)\b",
        r"\b(alone|by myself|in a group|in public|in private|in person|online|virtually|remotely)\b",
        r"\b(professional|personal|social|academic|business|casual|formal|informal) (setting|context|environment|situation|circumstance)\b",
        r"\b(in a|during a|at a) (meeting|conversation|discussion|argument|debate|negotiation|presentation|interview|date|gathering|party|event|ceremony|conference|workshop|class|session)\b",
        r"\b(emotional|stressful|relaxed|tense|peaceful|chaotic|busy|quiet|loud|crowded|empty|familiar|unfamiliar|comfortable|uncomfortable) (situation|environment|setting|atmosphere|surroundings)\b"
    ],

    "person:alec": [
        r"\b(alec)\b",
        r"\b(brother|little brother)\b",
        r"\b(younger brother)\b",
        r"\b(little a)\b",
    ],

    "person:caleb": [
        r"\b(caleb)\b",
        r"\b(caleob)\b",
        r"\b(best[ -]?friend|bestie|bff)\b",
        r"\b(like a brother)\b",
        r"\b(best homie|closest friend)\b",
    ],

    "person:kyle": [
        r"\b(kyle)\b",
        r"\b(brother|older brother)\b",
        r"\b(eldest brother)\b",
        r"\b(kmac)\b",
    ],

    "person:mom": [
        r"\b(mom|mother|mommy)\b",
        r"\b(my mom|my mother)\b",
        r"\b(dee|deirdre|dee[- ]?dee)\b",  # Replace with her actual name
    ],

    "person:dad": [
        r"\b(dad|father|daddy|pops|papa)\b",
        r"\b(my dad|my father)\b", 
        r"\b(colin)\b",  # Replace with his actual name
    ],

    "person:grandma_eileen": [
        r"\b(grandma|grandmother|granny|gran|suzie|granny suzie|eileen)\b", 
        r"\b(my grandma|my grandmother)\b",
        r"\b(grandma eileen)\b",  # If you use her last name
        r"\bmom's (mother|mom)\b",  # Specify which side of family if relevant
        r"\b(grandma mcgowan)\b"  # If you use her last name
    ],

    "person:grandma_wilma": [
        r"\b(grandma|grandmother|gran)\b", 
        r"\b(scottish gran(dma|dmother|ny)?)\b", 
        r"\b(my grandma|my grandmother)\b",
        r"\b(grandma wilma)\b",  # If you use her last name
        r"\bdad's (mother|mom)\b",  # Specify which side of family if relevant
        r"\b(grandma mckechnie)\b",  # If you use her last name
    ],

    "person:james": [
        r"\b(james|jimmy|jimbo|jamesy)\b",  
        r"\bjames hinton\b" 
    ],

    "person:jane": [
        r"\b(jane|janey|jane hinton)\b",  
    ],

    "person:samantha": [
        r"\b(samantha|samantha regan)\b",  
        r"\bex[- ]?wife\b"
        r"\bmy kids (mom|mother)\b",
        r"\bmother of my (kids|children)\b"
    ],

    "person:lily": [
        r"\b(lily|lily konigsberg)\b",
        r"\bex[- ]?girlfriend\b",
        r"\bmy ex\b",
    ],

    "person:jess": [
        r"\b(jess|jessica|borenkind)\b",
        r"\bmy girl\b",
        r"\bmy girlfriend\b",
    ],

    "person:waggener": [
        r"\b(waggener)\b",
        r"\bsam\b",
        r"\bmy friend waggener\b",
        r"\bfag-ner\b",
    ],

    "person:harry": [
        r"\b(harry|harold)\b",
    ],

    "person:tommy": [
        r"\btommy\b",
        r"\bt(ee)?[- ]?(dog|dawg)\b",
        r"\btommy leonard\b",
        r"\bmy best[- ]?friend in aa\b",
    ],

}
    
    # Clean the text by removing non-alphabetic characters and converting to lowercase
    text_lower = text.lower()
    
    # Calculate scores for each tag by counting keyword occurrences
    scores = {}
    for tag, patterns in regex_tag_patterns.items():
        match_count = 0
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            match_count += len(matches)

        if match_count > 0:
            scores[tag] = match_count

    
    # new approach with Context-Aware parsin
    military_patterns = regex_tag_patterns["military"]
    military_locations = ["somalia", "south sudan", "afghanistan", "iraq", "palestine", "syria", "ukraine"]
    
    for location in military_locations:
        if location in text_lower:
            # Look for any military term in a window around the location
            loc_index = text_lower.find(location)
            # Create a window 100 characters before and after the location mention
            window_start = max(0, loc_index - 100)
            window_end = min(len(text_lower), loc_index + 100)
            context_window = text_lower[window_start:window_end]
            
            # Use regex pattern matching properly
            context_has_military_term = False
            for pattern in military_patterns:
                # Apply each regex pattern to the context window
                if re.search(pattern, context_window):
                    context_has_military_term = True
                    break
                
            # If military term was found near the location
            if context_has_military_term:
                if "military" not in scores:
                    scores["military"] = 0
                scores["military"] += 2  # Give extra weight to this contextual match
                
                # Also add these countries as location tags
                if "location" not in scores:
                    scores["location"] = 0
                scores["location"] += 1


    # Return the top N tags with scores > 0, sorted by score (highest first)
    return sorted([k for k, v in scores.items() if v > 0], key=lambda k: -scores[k])[:top_n]




# ----------------------------------------- If you want to return tags w/ scores:----------------------------------------
    # sorted_tags_with_scores = sorted([(k, v) for k, v in scores.items() if v > 0], key=lambda item: -item[1])[:top_n]

    # return sorted_tags_with_scores
# -----------------------------------------------------------------------------------------------------------------------



# --- OpenAI Punctuation ---
# This function uses OpenAI to properly format and punctuate raw text
# Input: text (string) to format
# Output: formatted text with proper punctuation
def punctuate(text):
    client = openai.OpenAI()
    # Create a prompt asking the model to format the text
    prompt = (
        "Take this raw transcript and format it into organized, properly punctuated text. "
        "Keep the tone as is, preserve slang and profanity:\n\n"
        + text + "\n\nFormatted version:"
    )
    # Call the OpenAI API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1500
    )
    # Return the formatted text
    return response.choices[0].message.content.strip()

# --- Clean Whisper transcript ---
# This function cleans a transcript file by removing timestamps and joining lines
# Input: path (string) to the transcript file
# Output: cleaned text as a single string
def clean_transcript(path):
    # Read all lines from the file
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    # Remove timestamp markers using regex and strip whitespace
    content = [re.sub(r"\[\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}\.\d{3}\]", "", line).strip() for line in lines]
    # Join non-empty lines into a single string
    return " ".join(line for line in content if line)

# --- Main processing ---
# This function processes a transcript file into either a RAG memory chunk or SFT training example
# Inputs: 
#   txt_path (string): path to transcript file
#   title (string): title for the memory chunk
#   instruction (string): instruction for SFT mode
#   mode (string): "sft" or "rag"
#   output_path (string): path to save the output JSONL
# Output: formatted text content
def process(txt_path, title, instruction, mode, output_path="rag_memory_chunks.jsonl"):
    # Clean the transcript
    raw = clean_transcript(txt_path)
    # Format with proper punctuation
    formatted = punctuate(raw)

    # Create different output formats based on mode
    if mode == "sft":
        # For Supervised Fine-Tuning, create instruction-response pair
        chunk = {
            "instruction": instruction,
            "response": formatted
        }
    else:  # rag mode (default)
        # For RAG, include content with tags
        tags = suggest_tags(formatted)
        chunk = {
            "title": title,
            "content": formatted,
            "tags": tags
        }

# ----------------------------------------- If you want to return tags w/ scores:----------------------------------------
    #     tags_with_scores = suggest_tags(formatted)
        
    #     # Print the tags with their scores
    #     for tag, score in tags_with_scores:
    #         print(f"Tag: {tag}, Score: {score}")
        
    #     # Create a dictionary of tags with their scores
    #     tags_dict = {tag: score for tag, score in tags_with_scores}
        
    #     chunk = {
    #         "title": title,
    #         "content": formatted,
    #         "tags": [tag for tag, _ in tags_with_scores],  # Keep the original tags list
    #         "tag_scores": tags_dict  # Add the scores dictionary
    #     }

    #     # Append the chunk to the output file
    # with open(output_path, "a", encoding="utf-8") as f:
    #     f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    # return formatted
# -----------------------------------------------------------------------------------------------------------------------   

    # Append the chunk to the output file
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    return formatted

# --- CLI usage ---
# This section runs when the script is executed directly (not imported)
if __name__ == "__main__":
    # Check if enough command-line arguments are provided
    if len(sys.argv) < 5:
        print("Usage: python process.py <txt_path> <title> <instruction> <mode> [output_path]")
        sys.exit(1)

    # Parse command-line arguments
    txt_path = sys.argv[1]
    title = sys.argv[2]
    instruction = sys.argv[3]
    mode = sys.argv[4]
    output_path = sys.argv[5] if len(sys.argv) > 5 else "rag_memory_chunks.jsonl"

    # Process the transcript and print the result
    output = process(txt_path, title, instruction, mode, output_path)
    print(output)
