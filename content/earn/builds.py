"""Earn by Doing: the 12 starter builds as learn-by-doing workshops (brief → make → check → improve → ship).

Each build produces the deliverables its card promises ("You'll make …") as one Markdown document, with a guided
template (no AI) or a draft from the learner's own key. Every build also ships a practice pack and a worked example;
test/earn-builds.test.mjs runs each example through the same checks learners get, so the example always passes.
All businesses, people and numbers in the examples are invented. Original to Open Practice."""
from textwrap import dedent

def F(id, label, kind='text', ph='', req=True, opts=None, help='', blank=None, rows=3):
    return dict(id=id, label=label, kind=kind, ph=ph, required=req, opts=opts or [], help=help, blank=blank, rows=rows)

def H(title, pattern=None):
    """A required ## section."""
    return dict(t='re', re=r'^##\s*(' + (pattern or title) + ')', flags='im', label=f'Has a “{title}” section', fix=f'Add a heading line “## {title}” and fill it in.')

def RE(re, label, fix, flags='im'):
    return dict(t='re', re=re, flags=flags, label=label, fix=fix)

HONEST = dict(t='not', re=r"passive income|get rich|risk[- ]free|overnight|(?<!no |not |never |without )guaranteed? (?:results|income|sales|rankings?|leads|returns|profit)|\b(?:10|100)x\b",
              flags='i', label='No hype: no guaranteed results, passive income or overnight claims',
              fix='Delete the promise. Say what you will deliver and how you will check it instead.')
BLANKS = dict(t='blanks')
EXAMPLE_NOTE = '> Worked example. The business, people and numbers are invented to show the shape of a finished deliverable.\n\n'
d = lambda s: dedent(s).strip() + '\n'

BUILDS = [
# 01 ---------------------------------------------------------------------------------------------------------------
dict(num=1, slug='offer-sheet', track='First Customer', name='Offer Sheet Builder', emoji='🤝',
 h1='Make an offer someone can say yes to',
 desc='Free offer sheet workshop: narrow a problem, plan five buyer interviews, define the deliverable and test a first price before you build anything.',
 intro='Most first offers fail because they describe a skill, not a result for one kind of person. Here you write a niche brief, plan five short problem interviews, define exactly what you hand over, and set a price you can test by saying it out loud. The workshop takes about 20 minutes; the interviews take a week.',
 skills=['Choosing one buyer and one painful, repeated job', 'Writing a bounded offer with exclusions, timeline and revisions', 'Setting a price hypothesis and a rule for changing it'],
 makes=['Niche brief', 'Offer sheet', 'Price hypothesis'],
 fields=[F('skill', 'What can you already do well?', 'text', 'e.g. tidy spreadsheets and clear WhatsApp messages'),
         F('buyer', 'Who exactly is the buyer?', 'text', 'e.g. hair salon owners in one neighbourhood', help='One kind of person you can reach this week.'),
         F('problem', 'What painful, repeated job do they have?', 'text', 'e.g. WhatsApp booking enquiries go unanswered on busy days'),
         F('deliverable', 'What exactly will you hand over?', 'text', 'e.g. a quick-reply set and a booking script'),
         F('price', 'Your first price guess (with currency)', 'text', 'e.g. US$40 one-off setup'),
         F('proof', 'Any evidence the problem is real (optional)', 'textarea', 'e.g. two owners told me they lose Saturday bookings', req=False, rows=3)],
 prompt='Help me write an offer sheet in Markdown. Skill: {skill}. Buyer: {buyer}. Their problem: {problem}. Deliverable: {deliverable}. First price: {price}. Evidence so far: {proof}.\nUse exactly these ## sections: Niche brief, Problem interview (5 numbered open questions about past events, not opinions), The offer (what you get, exclusions, timeline in days, revisions, what I need from you), Price hypothesis (first price, why this number, how I will test it, the rule for changing it), Boundary, Evidence so far. Do not invent customers, quotes or results. Mark anything I must find out as [[to check]]. No hype.',
 template=d('''
    # Offer sheet: {deliverable} for {buyer}

    ## Niche brief
    - Buyer: {buyer}
    - The job they hate: {problem}
    - Where I can reach five of them this week: [[a place you can actually reach them, e.g. a market row, a group you already belong to]]
    - Why me: {skill}

    ## Problem interview
    1. Tell me about the last time this happened: {problem}. What did you do?
    2. [[a question about what it cost them: time, money or customers]]
    3. [[a question about what they have tried already]]
    4. [[a question about who decides and who pays]]
    5. If this were solved, what would be different next month?

    Notes after the interviews: [[what you heard, in their words, and how many said it hurts]]

    ## The offer
    - What you get: {deliverable}
    - Exclusions: [[what is not included]]
    - Timeline: [[number]] days from yes to delivery
    - Revisions: [[number]] rounds
    - What I need from you: [[access, files or an hour of your time]]

    ## Price hypothesis
    - First price: {price}
    - Why this number: [[hours it takes × your hourly rate, or what they pay now for a worse fix]]
    - How I will test it: [[e.g. say the price to five buyers and count who asks how to start]]
    - I will change the price if: [[a rule, e.g. all five say yes at once → raise it next time]]

    ## Boundary
    - No guaranteed results, no invented testimonials and no fake deadlines.
    - [[one limit specific to this offer]]

    ## Evidence so far
    {proof}
    [[what you have checked yourself, with dates]]
    '''),
 checks=[BLANKS, H('Niche brief'), H('Problem interview'), H('The offer', 'the offer|offer'), H('Price hypothesis'), H('Boundary'),
         dict(t='lines', match=r'^\d+[.)]\s', min=5, what='numbered interview questions'),
         RE(r'(exclusions?|not included)\s*:', 'Lists exclusions', 'Add “Exclusions: …” so the buyer knows where the job ends.'),
         RE(r'timeline\s*:.*\d', 'Timeline names a number of days', 'Write “Timeline: 5 days from yes to delivery”.'),
         RE(r'first price\s*:.*\d', 'First price is a real number', 'Write a number with a currency, e.g. “First price: US$40”.'),
         dict(t='has', field='buyer', name='buyer'), HONEST, dict(t='words', min=200, max=900)],
 selfcheck=['Could you name five real people who match the buyer line?', 'Are the interview questions about past events, not “would you buy”?', 'Would you be comfortable reading the boundary out loud to a buyer?'],
 tips=['If you cannot say where to find five buyers this week, the niche is too vague.', 'Ask about the last time the problem happened. Opinions about the future are cheap.', 'A price you are slightly nervous to say is usually closer to right.'],
 faq=[('Why interview before building anything?', 'Because the cheapest way to fail is on paper. Five 15-minute conversations tell you whether the problem is painful, who pays, and what words buyers use — all before you spend a week building.'),
      ('What if nobody likes my price?', 'That is data, not failure. Write down what they said, check whether the problem or the price was the issue, and change one thing at a time.')],
 example_values=dict(skill='tidy spreadsheets and clear WhatsApp messages', buyer='hair salon owners in Avondale', problem='WhatsApp booking enquiries go unanswered on busy Saturdays', deliverable='a quick-reply set and booking script', price='US$40 one-off setup'),
 example=EXAMPLE_NOTE + d('''
    # Offer sheet: a quick-reply set and booking script for hair salon owners in Avondale

    ## Niche brief
    - Buyer: hair salon owners in Avondale with two to six chairs
    - The job they hate: WhatsApp booking enquiries go unanswered on busy Saturdays
    - Where I can reach five of them this week: the salons on the two shopping rows I pass every day
    - Why me: I keep tidy spreadsheets and write clear WhatsApp messages for my church group

    ## Problem interview
    1. Tell me about the last Saturday when enquiries piled up. What did you do?
    2. How many of those people booked somewhere else, as far as you know?
    3. What have you tried already: a helper on the phone, a booking app, anything else?
    4. Who answers the business phone, and who would pay to fix this?
    5. If this were solved, what would be different next month?

    Notes after the interviews: four of five owners said Saturday mornings are the worst. Two said “by the time I answer, they have gone to the next salon”. One already uses quick replies and did not see a problem.

    ## The offer
    - What you get: a set of 12 WhatsApp Business quick replies, a booking script for the person on the phone, and a one-page price list image
    - Exclusions: no booking software, no paid adverts, no managing the phone for you
    - Timeline: 3 days from yes to delivery
    - Revisions: 2 rounds
    - What I need from you: 30 minutes to list your services and prices, and your current greeting message

    ## Price hypothesis
    - First price: US$40 one-off setup
    - Why this number: about four hours of work at US$10 an hour, and less than the value of two lost bookings
    - How I will test it: say the price to the five owners I interviewed and count who asks how to start
    - I will change the price if: four or more say yes at once, then the next offer is US$55

    ## Boundary
    - No guaranteed results, no invented testimonials and no fake deadlines.
    - I will not message the salon's customers myself or see their contact list.

    ## Evidence so far
    Two owners told me on 3 November that they lose Saturday bookings.
    I counted unanswered enquiries with one owner's permission: 9 waited more than an hour last Saturday.
    '''),
 files={'interview-notes.csv': 'date,buyer (role, no names),question,what they said (their words),how painful 1-5\n'},
 methods=[9, 18, 33, 39]),

# 02 ---------------------------------------------------------------------------------------------------------------
dict(num=2, slug='local-page-kit', track='Client Service', name='Local Business Page Kit', emoji='🏪',
 h1='Build a local business page',
 desc='Free local business page workshop: plan the copy, test a one-page demo on a phone and write the launch checklist and client handoff. No signup.',
 intro='A small business does not need a big website. It needs one fast page that says what it does, where it is, how much things cost and how to get in touch. You will write the page brief and copy, a test plan for the demo, a launch checklist and a handoff note the owner can actually use. Build the page itself with the free Website Generator, then come back to test it.',
 skills=['Writing page copy from the owner’s real services and prices', 'Testing a page on a phone: speed, contrast, form and links', 'Handing over a site the owner can run without you'],
 makes=['Tested demo', 'Launch checklist', 'Client handoff'],
 fields=[F('business', 'Business name and type', 'text', 'e.g. Tendai’s Shoe Repairs, a shoe and bag repair stall'),
         F('services', 'Services with prices (one per line)', 'textarea', 'Heel replacement — US$5\nZip repair — US$4\nBag strap — US$3', rows=4),
         F('area', 'Where is it, and when is it open?', 'text', 'e.g. Fife Avenue market, Mon–Sat 8:00–17:00'),
         F('contact', 'How should customers get in touch?', 'text', 'e.g. WhatsApp +263 7X XXX XXXX, no calls on Sunday'),
         F('proof', 'Proof the owner has given you permission to use', 'text', 'e.g. photos of real repairs, taken by the owner', req=False)],
 prompt='Write a Markdown kit for a one-page website for {business}. Services and prices:\n{services}\nLocation and hours: {area}. Contact: {contact}. Proof the owner approved: {proof}.\nUse exactly these ## sections: Page copy (a headline under 10 words, a one-line description, the services list with prices, location and hours, one contact button text), Demo test plan (phone loading, text contrast, form or button test, every link opened, spelling of prices and the phone number), Launch checklist (at least 8 - [ ] items), Client handoff (how to change a price, who owns the domain and accounts, what costs money later, how to get help), Boundary. Never invent reviews, awards or customer numbers.',
 template=d('''
    # Page kit: {business}

    ## Page copy
    Headline: [[under 10 words: what they do and for whom]]
    One line: [[one sentence a passer-by would understand]]

    Services and prices:
    {services}

    Where and when: {area}
    Contact button: [[the words on the button, e.g. “WhatsApp us to book”]] → {contact}
    Proof shown on the page: {proof}

    ## Demo test plan
    - Phone test: [[open the demo on a phone on mobile data; how many seconds until the text shows?]]
    - Contrast: [[can you read every line in sunlight?]]
    - Contact test: [[press the contact button; does it open the right number with a message ready?]]
    - Links: [[open every link; list any that fail]]
    - Facts: the owner checked every price, the hours and the number on [[date]]

    ## Launch checklist
    - [ ] Owner approved the copy in writing
    - [ ] Prices and phone number checked against the owner's list
    - [ ] Page loads on a phone in under [[number]] seconds
    - [ ] Every image is the owner's own, or free to use, and has alt text
    - [ ] Contact button tested from a second phone
    - [ ] The domain or free web address is registered in the owner's name
    - [ ] [[one more check specific to this business]]
    - [ ] Handoff note sent and read

    ## Client handoff
    - To change a price: [[the exact steps, in plain words]]
    - Who owns what: [[domain, hosting account, email: all in the owner's name]]
    - What may cost money later: [[e.g. a domain renewal each year; nothing else]]
    - How to get help: [[how to reach you and what you charge for changes, if anything]]

    ## Boundary
    - No invented reviews, awards or customer numbers. Only proof the owner gave permission for.
    - [[one more limit, e.g. I do not run paid adverts]]
    '''),
 checks=[BLANKS, H('Page copy'), H('Demo test plan', 'demo test plan|test plan'), H('Launch checklist'), H('Client handoff', 'client handoff|handoff'), H('Boundary'),
         RE(r'^headline\s*:\s*\S', 'Has a headline line', 'Add “Headline: …” under Page copy.'),
         dict(t='count', re=r'\d+(?:[.,]\d+)?', min=3, label='Shows real prices or numbers', fix='List services with prices the owner confirmed.'),
         dict(t='lines', match=r'^-\s*\[[ x]\]', min=8, what='checklist items (- [ ] …)'),
         RE(r'(owner.s name|in the owner)', 'Accounts stay in the owner’s name', 'Say that the domain and accounts are registered in the owner’s name.'),
         dict(t='not', re=r'\b(5[- ]star|award[- ]winning|#1|number one|best in (?:town|the city))\b', flags='i', label='No invented ratings or awards', fix='Remove ratings and awards unless the owner can show them.'),
         dict(t='has', field='business', name='business name'), HONEST, dict(t='words', min=220, max=1000)],
 selfcheck=['Did the owner check every price and the phone number themselves?', 'Could the owner change a price next month without you?', 'Did you test on a cheap phone on mobile data, not only on your laptop?'],
 tips=['Put the price list near the top. It is the question everyone has.', 'One contact route that works beats five that half work.', 'Keep a copy of the owner’s written approval with your evidence.'],
 faq=[('Do I need to code to do this?', 'No. The free Website Generator on Open Practice writes the page for you, and you read and change it. This workshop is about getting the content right and testing it properly.'),
      ('Who should own the domain?', 'The business owner, always. Register it in their name with their email. You can help them set it up, but they must be able to keep the site if you disappear.')],
 example_values=dict(business='Tendai’s Shoe Repairs, a shoe and bag repair stall', services='Heel replacement — US$5', area='Fife Avenue market, Mon–Sat 8:00–17:00', contact='WhatsApp only'),
 example=EXAMPLE_NOTE + d('''
    # Page kit: Tendai’s Shoe Repairs, a shoe and bag repair stall

    ## Page copy
    Headline: Shoe and bag repairs while you shop
    One line: Heels, zips and straps fixed at the Fife Avenue market, most jobs ready the same day.

    Services and prices:
    - Heel replacement — US$5
    - Zip repair — US$4
    - Bag strap — US$3
    - Resole (leather) — US$12

    Where and when: Fife Avenue market, row C, Mon–Sat 8:00–17:00
    Contact button: “WhatsApp Tendai to book” → WhatsApp only, replies within the hour
    Proof shown on the page: four before-and-after photos Tendai took of real repairs

    ## Demo test plan
    - Phone test: on a budget Android phone with mobile data, the text showed in 2 seconds and the photos in 4
    - Contrast: all text readable outdoors at noon; the grey caption was too light, so it is now dark brown
    - Contact test: the button opened WhatsApp with “Hello Tendai, I need a repair:” ready to send
    - Links: 3 links, all open; the map link pointed to the wrong row and was fixed
    - Facts: Tendai checked every price, the hours and the number on 4 November

    ## Launch checklist
    - [x] Owner approved the copy in writing
    - [x] Prices and phone number checked against the owner's list
    - [x] Page loads on a phone in under 3 seconds
    - [x] Every image is the owner's own, or free to use, and has alt text
    - [x] Contact button tested from a second phone
    - [x] The free web address is registered in the owner's name
    - [x] Opening hours repeated next to the button for Saturday shoppers
    - [ ] Handoff note sent and read

    ## Client handoff
    - To change a price: open the page editor, find the price list, change the number, press Publish. It takes two minutes.
    - Who owns what: the web address and the hosting account are in Tendai's name, with his email.
    - What may cost money later: nothing, unless he buys a custom domain (about US$12 a year).
    - How to get help: WhatsApp me; small text changes are free for the first month.

    ## Boundary
    - No invented reviews, awards or customer numbers. Only proof the owner gave permission for.
    - I do not run paid adverts or manage his WhatsApp.
    '''),
 files={'launch-checklist.md': '# Launch checklist\n\n- [ ] Owner approved the copy in writing\n- [ ] Prices and phone number checked against the owner\'s list\n- [ ] Loads on a phone on mobile data in under 3 seconds\n- [ ] Every image is the owner\'s own or free to use, with alt text\n- [ ] Contact button tested from a second phone\n- [ ] Domain or free address registered in the owner\'s name\n- [ ] Handoff note sent and read\n'},
 methods=[1, 2, 8, 20], extra_tools=['website-generator', 'landing-page-generator']),

# 03 ---------------------------------------------------------------------------------------------------------------
dict(num=3, slug='customer-reply-kit', track='Client Service', name='Customer Reply Kit', emoji='💬',
 h1='Create a customer-reply kit',
 desc='Free customer-reply kit workshop: turn repeated questions into a verified FAQ, a reply library and escalation rules a human controls. No signup.',
 intro='Every small business answers the same ten questions every week. A reply kit turns those into checked answers anyone on the team can send, plus clear rules for when a person must take over. You will collect real questions (with personal details removed), write the FAQ, a reply library with the right tone, and an escalation matrix.',
 skills=['Grouping real questions without copying anyone’s personal data', 'Writing short replies that answer first and stay accurate', 'Deciding which questions a human must always handle'],
 makes=['FAQ', 'Response library', 'Escalation matrix'],
 fields=[F('business', 'Business and what it sells', 'text', 'e.g. a home bakery selling cakes to order'),
         F('questions', 'The questions customers ask most (one per line, no names or numbers)', 'textarea', 'How much is a birthday cake?\nDo you deliver?\nCan you do sugar-free?', rows=5),
         F('facts', 'Facts the owner confirmed (prices, hours, policies)', 'textarea', 'Cakes from US$15\nDelivery within 5 km for US$2\nOrders need 3 days', rows=4),
         F('tone', 'Tone', 'select', opts=['Warm and short', 'Polite and formal', 'Friendly with emojis allowed'], req=False),
         F('human', 'What must always go to a person?', 'text', 'e.g. complaints, refunds, allergies, anything about money')],
 prompt='Create a customer-reply kit in Markdown for {business}. Real questions (anonymised):\n{questions}\nConfirmed facts:\n{facts}\nTone: {tone}. Always handled by a person: {human}.\nUse exactly these ## sections: FAQ (each question as ### and a short answer using only the confirmed facts), Response library (at least 6 ready-to-send replies, each under 60 words, labelled with when to use it), Escalation matrix (at least 4 lines: trigger → who handles it → how fast), Missing information (anything a reply needs that the facts do not contain), Boundary. Never invent a price, policy or promise. Mark unknowns as [[ask the owner]].',
 template=d('''
    # Customer reply kit: {business}

    ## FAQ
    Questions customers ask (no names or numbers kept):
    {questions}

    ### [[question 1, in the customer's words]]
    [[answer in 1–3 sentences, using only these facts:]]
    {facts}

    ### [[question 2]]
    [[answer]]

    ### [[question 3]]
    [[answer]]

    ## Response library
    Tone: {tone}
    - When someone asks the price: [[reply under 60 words]]
    - When someone asks about delivery: [[reply]]
    - When you cannot do what they ask: [[a kind no, with an alternative]]
    - When an order is confirmed: [[reply that repeats what, when and how much]]
    - When someone is upset: [[reply that thanks them and says a person will call]]
    - When you do not know the answer: [[reply that promises a time, not an answer]]

    ## Escalation matrix
    Always handled by a person: {human}
    - [[trigger, e.g. the word “refund”]] → [[who]] → [[within how long]]
    - [[trigger]] → [[who]] → [[how long]]
    - [[trigger]] → [[who]] → [[how long]]
    - [[trigger]] → [[who]] → [[how long]]

    ## Missing information
    [[anything a reply needs that the owner has not confirmed yet]]

    ## Boundary
    - Every price and policy here was confirmed by the owner. Nothing invented.
    - Customer names, numbers and messages were removed before writing this kit.
    '''),
 checks=[BLANKS, H('FAQ'), H('Response library'), H('Escalation matrix'), H('Missing information'), H('Boundary'),
         dict(t='lines', match=r'^###\s', min=3, what='FAQ questions (### …)'),
         dict(t='lines', match=r'^-\s*when ', min=6, what='library replies (- When …)'),
         dict(t='lines', match=r'→.*→', min=4, what='escalation rules (trigger → who → how fast)'),
         dict(t='not', re=r'\+?\d[\d ()-]{8,}\d|[\w.+-]+@[\w-]+\.[\w.]+', flags='', label='No phone numbers or email addresses copied in', fix='Remove personal contact details; use a placeholder like “the shop number”.'),
         dict(t='has', field='business', name='business'), HONEST, dict(t='words', min=220, max=1000)],
 selfcheck=['Is every price and policy one the owner confirmed?', 'Would the reply to an upset customer calm you down?', 'Does every escalation say who and how fast, not just “escalate”?'],
 tips=['Answer first, explain second. Most customers read only the first line.', '“I don’t know yet, I will reply by 3 pm” is a perfectly good reply.', 'Allergies, money and complaints go to a person. Every time.'],
 faq=[('Can I paste real customer chats into an AI tool?', 'Not with names, numbers or private details in them. Remove those first, or write the questions in your own words. The guided template needs no AI at all.'),
      ('Is this the same as a chatbot?', 'No. This kit is for people to use, and it is the foundation a chatbot would need later. Most small businesses get most of the benefit from the kit alone.')],
 example_values=dict(business='a home bakery selling cakes to order', questions='How much is a birthday cake?', facts='Cakes from US$15', human='complaints, refunds, allergies'),
 example=EXAMPLE_NOTE + d('''
    # Customer reply kit: a home bakery selling cakes to order

    ## FAQ
    Questions customers ask (no names or numbers kept): price, delivery, sugar-free options, how early to order, payment.

    ### How much is a birthday cake?
    Cakes start at US$15 for a 20 cm sponge. Fillings and writing are included; figures and photos cost extra.

    ### Do you deliver?
    Yes, within 5 km for US$2. Further away, you can collect from the house.

    ### How early do I need to order?
    Three days before. For weddings and orders over 30 people, two weeks.

    ## Response library
    Tone: Warm and short
    - When someone asks the price: Hello! Birthday cakes start at US$15 for a 20 cm sponge, writing included. What date is it for?
    - When someone asks about delivery: We deliver within 5 km for US$2, or you can collect. Which area are you in?
    - When you cannot do what they ask: I'm sorry, we can't do that one. We can do a vanilla cake with a printed photo instead. Would that work?
    - When an order is confirmed: Thank you! One chocolate cake, 20 cm, "Happy 7th Tino", Saturday at 10:00, US$17 with delivery.
    - When someone is upset: Thank you for telling us, and I'm sorry. The owner will call you today to sort it out.
    - When you do not know the answer: Good question. Let me check with the baker and reply by 3 pm.

    ## Escalation matrix
    Always handled by a person: complaints, refunds, allergies, anything about money
    - The words "allergy", "nuts" or "gluten" → the baker → before the order is accepted
    - Any complaint or refund request → the owner → a call the same day
    - Orders over 30 people → the owner → within 24 hours
    - Payment did not arrive → the owner → within 2 hours

    ## Missing information
    The owner has not confirmed whether sugar-free cakes are possible. Until then, the reply is "let me check".

    ## Boundary
    - Every price and policy here was confirmed by the owner. Nothing invented.
    - Customer names, numbers and messages were removed before writing this kit.
    '''),
 files={'escalation-matrix.csv': 'trigger (word or situation),who handles it,how fast,notes\n'},
 methods=[3, 4, 5, 29], extra_tools=['faq-generator', 'email-writer']),

# 04 ---------------------------------------------------------------------------------------------------------------
dict(num=4, slug='spreadsheet-cleanup', track='Data & Spreadsheets', name='Spreadsheet Cleanup Plan', emoji='🧹',
 h1='Clean a real spreadsheet safely',
 desc='Free spreadsheet cleaning workshop: write a rules log, clean a copy without leaking personal data and prove the result with a validation report.',
 intro='Cleaning a client’s spreadsheet is easy to get wrong in ways nobody notices until money is involved. Here you work on a copy, write down every rule before you apply it, and finish with a validation report that compares before and after. AI can suggest rules and formulas; the checks are done with counts and formulas, not trust.',
 skills=['Writing cleaning rules before touching the data', 'Protecting personal data while you work', 'Proving a clean-up with before-and-after counts'],
 makes=['Rules log', 'Cleaned file', 'Validation report'],
 fields=[F('sheet', 'What is the spreadsheet for?', 'text', 'e.g. a hardware shop’s stock list'),
         F('size', 'How big is it? (rows and columns)', 'text', 'e.g. 1,240 rows, 9 columns'),
         F('problems', 'What is wrong with it? (one per line)', 'textarea', 'Duplicate products\nPrices typed as text\nSupplier names spelled 3 ways', rows=4),
         F('personal', 'Does it contain personal data? Which columns?', 'text', 'e.g. supplier phone numbers in column H'),
         F('goal', 'What must the clean file be able to do?', 'text', 'e.g. total stock value by supplier')],
 prompt='Help me plan a safe spreadsheet clean-up in Markdown. Sheet: {sheet}, size {size}. Problems:\n{problems}\nPersonal data: {personal}. Goal: {goal}.\nUse exactly these ## sections: Safety first (work on a copy, how personal data is protected), Rules log (numbered rules: what, which column, why, the formula or method), Validation report (row count before and after, duplicates removed, values changed, totals before and after, three spot checks), Handoff (what the client receives and what they must check), Boundary. Never ask me to paste personal data into AI. Use [[measure this]] where I must count something.',
 template=d('''
    # Clean-up plan: {sheet}

    ## Safety first
    - I work on a copy named [[file name]]. The original is never edited.
    - Personal data: {personal}. [[how you protect it: hide or remove the column before using AI, never paste it anywhere]]
    - Size at the start: {size}

    ## Rules log
    Problems found:
    {problems}

    1. [[rule: what you change]] — column [[letter]] — why: [[reason]] — method: [[formula or step]]
    2. [[rule]] — column [[letter]] — why: [[reason]] — method: [[formula or step]]
    3. [[rule]] — column [[letter]] — why: [[reason]] — method: [[formula or step]]

    ## Validation report
    - Rows before: [[number]] · rows after: [[number]]
    - Duplicates removed: [[number]], listed in the tab “removed”
    - Values changed: [[number]], listed in the tab “changes”
    - Check total before: [[number]] · after: [[number]] · difference explained: [[why]]
    - Spot checks (three rows compared by hand): [[row numbers and result]]
    - The goal works: {goal} → [[the formula or pivot that proves it]]

    ## Handoff
    - The client receives: the cleaned copy, the rules log and this report
    - The client must check: [[the one or two things only they can confirm]]

    ## Boundary
    - Nothing was deleted without being listed. The original file is untouched.
    - No personal data was pasted into an AI tool.
    '''),
 checks=[BLANKS, H('Safety first'), H('Rules log'), H('Validation report'), H('Handoff'), H('Boundary'),
         dict(t='lines', match=r'^\d+[.)]\s', min=3, what='numbered cleaning rules'),
         RE(r'rows before\s*:\s*[\d,]+.*rows after\s*:\s*[\d,]+', 'Reports row counts before and after', 'Write “Rows before: 1,240 · rows after: 1,198”.'),
         RE(r'\bcopy\b', 'Works on a copy', 'Say that you work on a copy and never edit the original.'),
         RE(r'spot checks?', 'Includes hand spot checks', 'Compare three rows by hand and write the row numbers.'),
         dict(t='has', field='sheet', name='spreadsheet'), HONEST, dict(t='words', min=180, max=900)],
 selfcheck=['Could someone else repeat your clean-up from the rules log alone?', 'Is every removed row listed somewhere?', 'Did any personal data leave the file at any point?'],
 tips=['Count first. A before-and-after row count catches most disasters.', 'Never delete in place: move removed rows to their own tab.', 'AI is good at suggesting formulas. Check every one on five rows before using it.'],
 faq=[('Can AI clean the spreadsheet for me?', 'It can suggest rules and formulas, and that is useful. But the clean-up must be done with formulas you can check, and personal data must never be pasted into an AI tool.'),
      ('What does a client actually pay for here?', 'For trust: a file they can rely on and proof of what changed. The validation report is what makes the work worth paying for.')],
 example_values=dict(sheet='a hardware shop’s stock list', size='1,240 rows, 9 columns', personal='supplier phone numbers in column H', goal='total stock value by supplier'),
 example=EXAMPLE_NOTE + d('''
    # Clean-up plan: a hardware shop’s stock list

    ## Safety first
    - I work on a copy named stock-clean-2026-11-04.xlsx. The original is never edited.
    - Personal data: supplier phone numbers in column H. I hid column H before asking AI for formulas and never pasted any row.
    - Size at the start: 1,240 rows, 9 columns

    ## Rules log
    Problems found: duplicate products, prices typed as text, supplier names spelled three ways.

    1. Merge exact duplicates — column B (product code) — why: the same code appears twice — method: sort by code, compare rows, keep the newer count
    2. Convert prices to numbers — column E — why: 312 prices were text — method: =VALUE(SUBSTITUTE(E2,"$",""))
    3. One spelling per supplier — column G — why: "Hardline", "Hard Line" and "HARDLINE" — method: lookup table in the tab "suppliers"

    ## Validation report
    - Rows before: 1,240 · rows after: 1,198
    - Duplicates removed: 42, listed in the tab “removed”
    - Values changed: 391, listed in the tab “changes”
    - Check total before: 1,240 rows of stock · after: 1,198 · difference explained: the 42 duplicates, each checked
    - Spot checks (three rows compared by hand): rows 15, 402 and 1,103 match the paper stock book
    - The goal works: total stock value by supplier → a pivot table on column G, total US$18,406

    ## Handoff
    - The client receives: the cleaned copy, the rules log and this report
    - The client must check: the 6 products where the two duplicate counts disagreed

    ## Boundary
    - Nothing was deleted without being listed. The original file is untouched.
    - No personal data was pasted into an AI tool.
    '''),
 files={'rules-log.csv': 'rule #,what changes,column,why,formula or method,rows affected\n', 'validation-report.csv': 'check,before,after,difference explained\nrow count,,,\nduplicates removed,,,\nvalues changed,,,\ncheck total,,,\n'},
 methods=[16, 23, 27], extra_tools=['google-sheets-script']),

# 05 ---------------------------------------------------------------------------------------------------------------
dict(num=5, slug='clip-pack', track='Creative Production', name='Clip Pack Planner', emoji='🎬',
 h1='Turn one recording into a clip pack',
 desc='Free clip pack workshop: pick short moments from a long video, write captions, keep a rights log and get approval before anything is posted.',
 intro='Creators and small organisations record long videos and never cut them down. A clip pack turns one long recording into a few short, captioned moments, with a rights log and an approval sheet so nothing goes out without permission. You plan the pack here; cut the clips in any free editor.',
 skills=['Finding moments that make sense without the rest of the video', 'Writing accurate captions and hooks', 'Tracking rights and approval before publishing'],
 makes=['Clips', 'Captions', 'Rights log', 'Approval sheet'],
 fields=[F('source', 'What is the long video?', 'text', 'e.g. a 45-minute church youth talk on saving money'),
         F('owner', 'Who owns it, and did they say yes in writing?', 'text', 'e.g. the youth pastor, written yes on WhatsApp'),
         F('audience', 'Who should the clips reach?', 'text', 'e.g. 16–25-year-olds who follow the church page'),
         F('moments', 'Moments you noted (timestamp + what happens)', 'textarea', '04:10 the 50-cent jar story\n17:30 three rules for a first pay cheque\n31:05 audience question', rows=4),
         F('platform', 'Where will they be posted?', 'text', 'e.g. Facebook Reels and WhatsApp Status')],
 prompt='Plan a clip pack in Markdown from this long video: {source}. Owner and permission: {owner}. Audience: {audience}. Platform: {platform}. Moments I noted:\n{moments}\nUse exactly these ## sections: Clips (at least 3, each ### with start and end timestamps, under 60 seconds, why it stands alone), Captions (one per clip: a hook line under 12 words and an accurate caption that does not exaggerate what was said), Rights log (music, faces, logos, other people speaking: who allowed what), Approval sheet (each clip: approved by, date, changes asked for), Boundary. Never invent quotes.',
 template=d('''
    # Clip pack: {source}

    ## Clips
    Moments noted:
    {moments}

    ### Clip 1: [[short title]]
    [[start mm:ss]] – [[end mm:ss]] · why it stands alone: [[reason]]

    ### Clip 2: [[short title]]
    [[start]] – [[end]] · why it stands alone: [[reason]]

    ### Clip 3: [[short title]]
    [[start]] – [[end]] · why it stands alone: [[reason]]

    ## Captions
    For {audience} on {platform}
    - Clip 1 hook: [[under 12 words]] · caption: [[what was actually said, no exaggeration]]
    - Clip 2 hook: [[hook]] · caption: [[caption]]
    - Clip 3 hook: [[hook]] · caption: [[caption]]

    ## Rights log
    - Video owner: {owner}
    - Music in the background: [[none / whose / allowed?]]
    - Other people seen or heard: [[who, and did they agree?]]
    - Logos or other people's content on screen: [[what, and is it allowed?]]

    ## Approval sheet
    - Clip 1: approved by [[name or role]] on [[date]] · changes: [[none / what]]
    - Clip 2: approved by [[name or role]] on [[date]] · changes: [[changes]]
    - Clip 3: approved by [[name or role]] on [[date]] · changes: [[changes]]

    ## Boundary
    - Nothing is posted before the owner approves it. No invented quotes.
    - [[one more limit, e.g. no faces of minors without a parent's written yes]]
    '''),
 checks=[BLANKS, H('Clips'), H('Captions'), H('Rights log'), H('Approval sheet'), H('Boundary'),
         dict(t='count', re=r'\b\d{1,2}:\d{2}\b', min=6, label='Every clip has start and end timestamps', fix='Write start and end times like 04:10 – 04:52.'),
         dict(t='lines', match=r'hook\s*:', min=3, what='clip hooks'),
         dict(t='lines', match=r'approved by', min=3, what='approval lines'),
         RE(r'music', 'Rights log covers music', 'Say whether there is music and whether it is allowed.'),
         dict(t='has', field='source', name='source video'), HONEST, dict(t='words', min=180, max=900)],
 selfcheck=['Does each clip make sense to someone who never saw the full video?', 'Does every caption match what was actually said?', 'Do you have written permission for every person and song in the clips?'],
 tips=['The best clips start mid-thought, with the interesting sentence first.', 'Captions are read with the sound off. Make them carry the meaning.', 'Background music is the most common rights problem. Check it first.'],
 faq=[('Can I clip any video I find online?', 'No. Only videos whose owner has said yes in writing. For practice, use a video you recorded yourself.'),
      ('Which free tools cut clips?', 'Any free editor you already have works: the phone’s built-in editor, CapCut’s free tier or Shotcut on a computer. The skill is choosing the moments.')],
 example_values=dict(source='a 45-minute youth talk on saving money', owner='the youth pastor, written yes on WhatsApp', audience='16–25-year-olds', platform='Facebook Reels and WhatsApp Status'),
 example=EXAMPLE_NOTE + d('''
    # Clip pack: a 45-minute youth talk on saving money

    ## Clips
    Moments noted: the 50-cent jar story, three rules for a first pay cheque, a question from the audience.

    ### Clip 1: The 50-cent jar
    04:10 – 04:52 · why it stands alone: a complete story with a clear ending

    ### Clip 2: Three rules for your first pay
    17:30 – 18:25 · why it stands alone: a numbered list people can screenshot

    ### Clip 3: "What if my family needs the money?"
    31:05 – 31:58 · why it stands alone: a real question and a short honest answer

    ## Captions
    For 16–25-year-olds on Facebook Reels and WhatsApp Status
    - Clip 1 hook: She saved one coin a day for a year · caption: Sister Rumbi's 50-cent jar, and what she bought with it.
    - Clip 2 hook: Three rules before you spend your first pay · caption: Pay yourself first, wait a week for big buys, tell one person your plan.
    - Clip 3 hook: When family asks for your savings · caption: A question from the floor and the pastor's answer, unedited.

    ## Rights log
    - Video owner: the youth pastor, written yes on WhatsApp on 2 November
    - Music in the background: none in the chosen clips
    - Other people seen or heard: the person asking in clip 3 agreed in writing; her face is cropped out
    - Logos or other people's content on screen: a bank poster at 17:40, cropped out to be safe

    ## Approval sheet
    - Clip 1: approved by the youth pastor on 5 November · changes: none
    - Clip 2: approved by the youth pastor on 5 November · changes: fix the spelling of "cheque"
    - Clip 3: approved by the youth pastor on 6 November · changes: start two seconds later

    ## Boundary
    - Nothing is posted before the owner approves it. No invented quotes.
    - No faces of anyone under 18 without a parent's written yes.
    '''),
 files={'rights-log.csv': 'item (music, person, logo),where (timestamp),who allowed it,how (written/verbal),date\n', 'approval-sheet.csv': 'clip,start,end,approved by,date,changes asked for\n'},
 methods=[6, 13, 36], extra_tools=['viral-hook-generator', 'tiktok-script']),

# 06 ---------------------------------------------------------------------------------------------------------------
dict(num=6, slug='article-refresh', track='Research & Content', name='Article Refresh Report', emoji='📰',
 h1='Refresh an outdated article',
 desc='Free article refresh workshop: check every claim against a source, rewrite what is out of date and hand over a change report the owner can trust.',
 intro='Old articles quietly lose readers because their facts, links and examples go stale. A refresh keeps what still works, fixes what does not, and proves every change. You will log sources for each claim you check, list the changes, and write a change report. AI can suggest rewrites; it cannot be the source.',
 skills=['Checking claims against primary sources', 'Rewriting only what needs rewriting', 'Reporting changes so the owner can approve them fast'],
 makes=['Source log', 'Revised article', 'Change report'],
 fields=[F('article', 'Which article, and how old is it?', 'text', 'e.g. “How to register a small business” blog post, written in 2022'),
         F('owner', 'Whose is it?', 'text', 'e.g. a local accountant’s blog (practice: use your own old post)'),
         F('claims', 'Claims or facts that may be out of date (one per line)', 'textarea', 'Registration costs US$X\nThe office is at Y\nForm Z is required', rows=4),
         F('reader', 'Who reads it, and what do they need?', 'text', 'e.g. first-time founders who want the steps in order')],
 prompt='Help me refresh an outdated article and document it in Markdown. Article: {article}. Owner: {owner}. Reader: {reader}. Claims that may be stale:\n{claims}\nUse exactly these ## sections: Source log (each claim: still true / changed / could not verify, with the primary source name and the date checked), Changes (numbered: before → after → why, plus internal links added or fixed), Revised sections (rewrite only the changed parts, plain language), Change report (a short note for the owner: what changed, what was kept, what they must confirm), Boundary. Never invent a source or a fact; write [[verify]] instead.',
 template=d('''
    # Article refresh: {article}

    ## Source log
    Claims to check:
    {claims}

    - Claim 1: [[the claim]] → [[still true / changed / could not verify]] · source: [[primary source name]] · checked [[date]]
    - Claim 2: [[claim]] → [[result]] · source: [[source]] · checked [[date]]
    - Claim 3: [[claim]] → [[result]] · source: [[source]] · checked [[date]]

    ## Changes
    1. [[before]] → [[after]] · why: [[reason]]
    2. [[before]] → [[after]] · why: [[reason]]
    3. [[before]] → [[after]] · why: [[reason]]
    - Internal links added or fixed: [[which pages on the same site now link here, or from here]]

    ## Revised sections
    Written for: {reader}
    [[the rewritten paragraphs only, in plain language]]

    ## Change report
    For {owner}:
    - Changed: [[summary]]
    - Kept as it was: [[what still works and why]]
    - Please confirm: [[anything only the owner can confirm]]

    ## Boundary
    - Every changed fact has a named source and a date. Nothing is invented.
    - An AI tool was not used as a source for any fact.
    '''),
 checks=[BLANKS, H('Source log'), H('Changes'), H('Revised sections', 'revised sections?|revised article'), H('Change report'), H('Boundary'),
         dict(t='lines', match=r'source\s*:', min=3, what='claims with a named source'),
         dict(t='lines', match=r'^\d+[.)]\s.*→', min=3, what='numbered changes (before → after)'),
         dict(t='count', re=r'checked\s+\S+', min=3, label='Each claim has a date checked', fix='Add “checked 4 November 2026” to each claim.'),
         dict(t='has', field='article', name='article'), HONEST, dict(t='words', min=180, max=1200)],
 selfcheck=['Could the owner open every source you named and find the same fact?', 'Did you keep the parts that were still right?', 'Is the change report short enough to read on a phone?'],
 tips=['Go to the primary source: the agency, the law, the company’s own page.', '“Could not verify” is an honest result. Say so rather than guess.', 'Most refreshes change 10–20% of an article. Rewriting everything hides your work.'],
 faq=[('Can AI tell me if a fact is still true?', 'No. It can help you find what to check and suggest wording, but it is not a source. Every fact you change needs a named source you opened yourself.'),
      ('Whose article should I practise on?', 'Your own old writing, or a public article you refresh privately as a sample. Never publish a refreshed version of someone else’s article without their permission.')],
 example_values=dict(article='“How to open a market stall” guide, written in 2022', owner='a community business blog', reader='first-time traders who want the steps in order'),
 example=EXAMPLE_NOTE + d('''
    # Article refresh: “How to open a market stall” guide, written in 2022

    ## Source log
    Claims to check: the stall licence fee, where to apply, the opening hours rule.

    - Claim 1: the licence fee is US$10 a month → changed · source: the town council's 2026 fee schedule · checked 4 November 2026
    - Claim 2: apply at the market office → still true · source: phone call to the market office · checked 4 November 2026
    - Claim 3: stalls may open at 6:00 → could not verify · source: council by-laws page (not updated since 2023) · checked 4 November 2026

    ## Changes
    1. "US$10 a month" → "US$12 a month (2026 schedule)" · why: the fee went up in January
    2. A dead link to the old council site → the current fee schedule page · why: the old link returns an error
    3. "Bring three photos" → "Bring two photos and your ID" · why: the market office said so on the phone
    - Internal links added or fixed: linked to the blog's budgeting post from step 4, and fixed a link to the old contact page

    ## Revised sections
    Written for: first-time traders who want the steps in order
    Step 2 now reads: Go to the market office with two photos and your ID. The licence costs US$12 a month under the 2026 fee schedule. Ask about opening hours when you apply, because the published rule may be out of date.

    ## Change report
    For a community business blog:
    - Changed: the fee, one dead link and the documents list
    - Kept as it was: the step order and the budgeting section, which are still accurate
    - Please confirm: the opening-hours rule, which no current source states

    ## Boundary
    - Every changed fact has a named source and a date. Nothing is invented.
    - An AI tool was not used as a source for any fact.
    '''),
 files={'source-log.csv': 'claim,result (still true / changed / could not verify),primary source,date checked,link or reference\n'},
 methods=[11, 19, 38], extra_tools=['blog-post-writer']),

# 07 ---------------------------------------------------------------------------------------------------------------
dict(num=7, slug='content-month', track='Retainer Service', name='Monthly Content Pack', emoji='🗓️',
 h1='Package a month of social content',
 desc='Free monthly content workshop: plan four weeks of posts from real business facts, draft them in the right voice and run an approval calendar.',
 intro='Small businesses know they should post, and stop after a week. A monthly pack fixes that with a simple system: themes from real facts, drafts in the owner’s voice, and an approval calendar so the owner says yes once a week, not every day. You will build the system, write the first drafts and set up the calendar.',
 skills=['Turning real business facts into post ideas', 'Writing in someone else’s voice without inventing claims', 'Running approvals so nothing goes out unchecked'],
 makes=['Content system', 'Drafts', 'Approval calendar'],
 fields=[F('business', 'Business and what it sells', 'text', 'e.g. a tailoring shop that makes work uniforms and suits', help='One line.'),
         F('facts', 'Real facts to draw on (one per line)', 'textarea', 'Suits ready in 7 days\nWe alter clothes bought elsewhere\nOpen since 2015', rows=4),
         F('voice', 'How does the owner talk?', 'text', 'e.g. proud of the craft, a bit funny, never pushy'),
         F('channel', 'Where will posts go, and how often?', 'text', 'e.g. Facebook page and WhatsApp Status, 3 times a week')],
 prompt='Build a monthly content pack in Markdown for {business}. Real facts:\n{facts}\nVoice: {voice}. Channel and frequency: {channel}.\nUse exactly these ## sections: Content system (4 weekly themes, each tied to a real fact; the rule for what never gets posted), Drafts (at least 4 drafts, each ### with the week, the draft under 80 words, a Visual: line with a photo or graphic brief, and the fact it is based on), Approval calendar (week by week: drafts sent on, owner replies by, posting days), Measures (2 or 3 things to count, e.g. enquiries that mention a post), Boundary. Never invent offers, prices, reviews or customer stories.',
 template=d('''
    # Monthly content pack: {business}

    ## Content system
    Real facts:
    {facts}

    - Week 1 theme: [[theme]] · based on: [[fact]]
    - Week 2 theme: [[theme]] · based on: [[fact]]
    - Week 3 theme: [[theme]] · based on: [[fact]]
    - Week 4 theme: [[theme]] · based on: [[fact]]
    - Never posted: [[e.g. customer photos without a yes, prices not confirmed, other businesses]]

    ## Drafts
    Voice: {voice}

    ### Week 1
    [[draft under 80 words]]
    Visual: [[photo or graphic idea the owner can shoot on a phone]]
    Based on: [[fact]]

    ### Week 2
    [[draft]]
    Visual: [[photo or graphic idea]]
    Based on: [[fact]]

    ### Week 3
    [[draft]]
    Visual: [[photo or graphic idea]]
    Based on: [[fact]]

    ### Week 4
    [[draft]]
    Visual: [[photo or graphic idea]]
    Based on: [[fact]]

    ## Approval calendar
    Channel: {channel}
    - Drafts sent to the owner every [[day]] by [[time]]
    - Owner replies by [[day]]; no reply means [[nothing is posted]]
    - Posting days: [[days]]

    ## Measures
    - [[something to count, e.g. enquiries that mention a post]]
    - [[a second measure]]

    ## Boundary
    - Every post is based on a fact the owner confirmed. No invented offers, prices or reviews.
    - Nothing is posted without the owner's approval.
    '''),
 checks=[BLANKS, H('Content system'), H('Drafts'), H('Approval calendar'), H('Measures'), H('Boundary'),
         dict(t='lines', match=r'^###\s*week', min=4, what='weekly drafts (### Week …)'),
         dict(t='lines', match=r'based on\s*:', min=8, what='themes and drafts tied to a fact'),
         dict(t='lines', match=r'^visual\s*:', min=4, what='visual briefs (Visual: …)'),
         RE(r'no reply means', 'Says what happens if the owner does not reply', 'Add “no reply means nothing is posted”.'),
         dict(t='has', field='business', name='business'), HONEST, dict(t='words', min=220, max=1100)],
 selfcheck=['Is every draft based on a fact the owner gave you?', 'Would the owner recognise their own voice?', 'Is approving the week a single, quick step for the owner?'],
 tips=['Four themes a month is plenty. Variety comes from the details, not the themes.', '“No reply means nothing is posted” protects you and the owner.', 'Count enquiries, not likes. Ask new customers where they heard about the business.'],
 faq=[('Do I need to post every day?', 'No. Three good posts a week that the owner approved beat daily filler. The system matters more than the volume.'),
      ('Can AI write all the posts?', 'It can draft them from the facts you give it, and the guided template works without it. Either way, every post is checked against a real fact and approved by the owner.')],
 example_values=dict(business='a tailoring shop that makes work uniforms and suits', facts='Suits ready in 7 days', voice='proud of the craft, a bit funny', channel='Facebook page and WhatsApp Status, 3 times a week'),
 example=EXAMPLE_NOTE + d('''
    # Monthly content pack: a tailoring shop that makes work uniforms and suits

    ## Content system
    Real facts: suits ready in 7 days, alterations on clothes bought elsewhere, open since 2015, two tailors with 30 years between them.

    - Week 1 theme: behind the seams · based on: two tailors with 30 years between them
    - Week 2 theme: fix what you already own · based on: alterations on clothes bought elsewhere
    - Week 3 theme: seven days to a suit · based on: suits ready in 7 days
    - Week 4 theme: ten years on the same corner · based on: open since 2015
    - Never posted: customer photos without a written yes, unconfirmed prices, comments about other shops

    ## Drafts
    Voice: proud of the craft, a bit funny, never pushy

    ### Week 1
    Baba Moyo has been cutting cloth since before most of our customers were born. Mai Tsitsi checks every buttonhole twice. Between them: 30 years and very strong opinions about lapels.
    Visual: both tailors at the cutting table, hands only
    Based on: two tailors with 30 years between them

    ### Week 2
    Bought a jacket that almost fits? Bring it in. We take in, let out, shorten and rescue clothes from any shop. Your favourite shirt deserves a second life.
    Visual: a before-and-after of a jacket taken in at the waist
    Based on: alterations on clothes bought elsewhere

    ### Week 3
    Monday: measurements. Wednesday: first fitting. Next Monday: you walk out in a suit made for you. Seven days, no shortcuts.
    Visual: three photos, one per fitting day, of the same suit
    Based on: suits ready in 7 days

    ### Week 4
    Same corner, same scissors, since 2015. Thank you to everyone who keeps walking up our steps.
    Visual: the shop front in morning light
    Based on: open since 2015

    ## Approval calendar
    Channel: Facebook page and WhatsApp Status, 3 times a week
    - Drafts sent to the owner every Friday by 16:00
    - Owner replies by Sunday; no reply means nothing is posted
    - Posting days: Monday, Wednesday, Friday

    ## Measures
    - Enquiries that mention a post, counted in a notebook at the counter
    - Alteration jobs per week, compared with last month

    ## Boundary
    - Every post is based on a fact the owner confirmed. No invented offers, prices or reviews.
    - Nothing is posted without the owner's approval.
    '''),
 files={'approval-calendar.csv': 'week,theme,draft sent (date),approved by,approved on,posting day,channel,notes\n'},
 methods=[14, 12, 2], extra_tools=['hashtag-generator', 'viral-hook-generator']),

# 08 ---------------------------------------------------------------------------------------------------------------
dict(num=8, slug='journey-audit', track='Sales & Research', name='Customer Journey Audit', emoji='🔎',
 h1='Audit a public customer journey',
 desc='Free customer journey audit workshop: walk the path a real customer takes, collect evidence, rank fixes by effort and impact and mock one up.',
 intro='Businesses lose customers at small, fixable moments: a broken link, a slow reply, a price you cannot find. A journey audit walks that path as a customer would, records what happens with evidence, and ranks fixes by how much they matter and how hard they are. You finish with a short mock-up of the top fix. Audit only public touchpoints, or a business that asked you to.',
 skills=['Walking a journey as a customer and recording evidence', 'Ranking fixes by impact and effort', 'Showing one fix instead of describing it'],
 makes=['Evidence pack', 'Prioritized fixes', 'Mini-demo'],
 fields=[F('business', 'Which business, and did they ask for this?', 'text', 'e.g. a driving instructor, practice audit with his permission'),
         F('goal', 'What is the customer trying to do?', 'text', 'e.g. book a first lesson'),
         F('steps', 'Steps you took, in order (one per line)', 'textarea', 'Searched “driving lessons Harare”\nOpened their Facebook page\nSent a WhatsApp at 10:05', rows=5),
         F('found', 'What went wrong or was slow?', 'textarea', 'No prices anywhere\nReply came after 26 hours', rows=3)],
 prompt='Help me write a customer journey audit in Markdown. Business: {business}. Customer goal: {goal}. Steps I took:\n{steps}\nWhat went wrong:\n{found}\nUse exactly these ## sections: Journey (numbered steps with what happened and the evidence: screenshot name, time, date), Evidence pack (what I captured and where it is stored), Prioritised fixes (at least 4, each: fix · impact high/medium/low · effort high/medium/low · why), Mini-demo (a before and after mock-up of the top fix, in words), Boundary. Only report what I observed; do not guess at the business’s numbers.',
 template=d('''
    # Journey audit: {business}

    ## Journey
    Customer goal: {goal}
    Steps taken:
    {steps}

    1. [[step]] → [[what happened]] · evidence: [[screenshot name, time and date]]
    2. [[step]] → [[what happened]] · evidence: [[evidence]]
    3. [[step]] → [[what happened]] · evidence: [[evidence]]
    4. [[step]] → [[what happened]] · evidence: [[evidence]]

    ## Evidence pack
    Problems seen:
    {found}
    Stored in: [[folder name]] · [[number]] screenshots, all from public pages or with permission

    ## Prioritised fixes
    - [[fix]] · impact: [[high/medium/low]] · effort: [[high/medium/low]] · why: [[reason]]
    - [[fix]] · impact: [[impact]] · effort: [[effort]] · why: [[reason]]
    - [[fix]] · impact: [[impact]] · effort: [[effort]] · why: [[reason]]
    - [[fix]] · impact: [[impact]] · effort: [[effort]] · why: [[reason]]

    ## Mini-demo
    Top fix: [[the fix]]
    Before: [[what a customer sees now]]
    After: [[what they would see]]

    ## Boundary
    - Only public touchpoints were used, or the business asked for this audit. No fake enquiries that waste staff time.
    - I report what I observed. I do not guess at the business's sales or numbers.
    '''),
 checks=[BLANKS, H('Journey'), H('Evidence pack'), H('Prioritised fixes'), H('Mini-demo'), H('Boundary'),
         dict(t='lines', match=r'^\d+[.)]\s.*evidence\s*:', min=4, what='journey steps with evidence'),
         dict(t='lines', match=r'impact\s*:\s*(high|medium|low).*effort\s*:\s*(high|medium|low)', min=4, what='fixes rated for impact and effort'),
         RE(r'^before\s*:.*\n(?:.*\n)?^after\s*:', 'Mini-demo shows before and after', 'Write a “Before:” line and an “After:” line for the top fix.'),
         dict(t='has', field='goal', name='customer goal'), HONEST, dict(t='words', min=200, max=1000)],
 selfcheck=['Could the owner repeat every step and see the same thing?', 'Is the top fix high impact and low effort, or did you choose the interesting one?', 'Did you avoid wasting staff time with fake requests?'],
 tips=['Time everything. “Reply after 26 hours” is more persuasive than “slow reply”.', 'Lead with the cheapest fix that matters. It earns trust for the rest.', 'One mock-up beats three paragraphs of advice.'],
 faq=[('Is it fair to audit a business that did not ask?', 'Looking at public pages is fine. Sending fake enquiries that take up staff time is not. If you need to test a reply, say who you are, or audit a business that agreed.'),
      ('How do I turn this into paid work?', 'Send the owner the top three fixes free, with evidence, and offer to make them. The audit shows you understand their business before you ask for anything.')],
 example_values=dict(business='a driving instructor, practice audit with his permission', goal='book a first lesson'),
 example=EXAMPLE_NOTE + d('''
    # Journey audit: a driving instructor, practice audit with his permission

    ## Journey
    Customer goal: book a first lesson
    Steps taken: searched, opened the Facebook page, sent a WhatsApp, waited for a reply.

    1. Searched "driving lessons Belvedere" → the page appears fourth, with no photo · evidence: 01-search.png, 10:01, 4 November
    2. Opened the Facebook page → last post from March, no prices · evidence: 02-page.png, 10:03, 4 November
    3. Sent "How much is a first lesson?" on WhatsApp → no automatic greeting · evidence: 03-message.png, 10:05, 4 November
    4. Waited for a reply → reply after 26 hours, asking me to call · evidence: 04-reply.png, 12:11, 5 November

    ## Evidence pack
    Problems seen: no prices anywhere, a reply after 26 hours, old posts.
    Stored in: audit-instructor-nov · 4 screenshots, all from public pages or with permission

    ## Prioritised fixes
    - Add a WhatsApp Business greeting with prices and lesson times · impact: high · effort: low · why: answers the first question instantly
    - Pin a post with prices and the booking steps · impact: high · effort: low · why: the page has no prices today
    - Reply within two hours on weekdays · impact: high · effort: medium · why: a learner waiting 26 hours books elsewhere
    - Post one learner pass photo a month, with permission · impact: medium · effort: low · why: the page looks inactive

    ## Mini-demo
    Top fix: a WhatsApp Business greeting
    Before: silence until he is free to type, sometimes a day later.
    After: "Hello! First lesson US$15, 45 minutes, Mon–Sat. Reply with a day and time and I will confirm today."

    ## Boundary
    - Only public touchpoints were used, or the business asked for this audit. No fake enquiries that waste staff time.
    - I report what I observed. I do not guess at the business's sales or numbers.
    '''),
 files={'evidence-pack.csv': 'step,what happened,screenshot file,time,date,public or permitted\n', 'fix-priority.csv': 'fix,impact (high/medium/low),effort (high/medium/low),why,owner decision\n'},
 methods=[18, 20, 21], extra_tools=['swot-analysis']),

# 09 ---------------------------------------------------------------------------------------------------------------
dict(num=9, slug='workflow-map', track='Automation', name='Workflow Map & Test Run', emoji='⚙️',
 h1='Map and prototype one workflow',
 desc='Free workflow automation workshop: map a repeated task step by step, mark where a human decides, test it on sample data and write handoff notes.',
 intro='Automation that nobody understands breaks the first time something unusual happens. Start with a map: every step, every decision, every place data moves. Then run the workflow by hand or with a free tool on sample data, note what failed, and write handoff notes so someone else can run it. The map is the product; the tool is a detail.',
 skills=['Mapping a process step by step, with inputs and outputs', 'Marking where a human must decide', 'Testing on sample data and writing handoff notes'],
 makes=['Process map', 'Test run', 'Handoff notes'],
 fields=[F('task', 'Which repeated task?', 'text', 'e.g. turning order messages into a delivery list each morning'),
         F('trigger', 'What starts it?', 'text', 'e.g. a new order message on WhatsApp'),
         F('steps', 'Steps today, in order (one per line)', 'textarea', 'Read the message\nCopy name, item, address into a sheet\nGroup by area\nSend the list to the driver', rows=5),
         F('tool', 'Free tool you will prototype with', 'select', opts=['By hand first (no tool)', 'Google Sheets formulas', 'A free automation tier (Zapier, Make, n8n)', 'A small script'], req=False),
         F('data', 'Personal data involved', 'text', 'e.g. customer names, addresses, phone numbers')],
 prompt='Help me map and test a workflow in Markdown. Task: {task}. Trigger: {trigger}. Steps today:\n{steps}\nPrototype tool: {tool}. Personal data: {data}.\nUse exactly these ## sections: Process map (numbered steps: input → action → output, with [HUMAN] on any step where a person decides), Test run (sample data used, at least 3 test cases including one unusual case, expected vs actual result), Failure plan (what happens when a step fails, who is told), Handoff notes (how to run it, how to stop it, where data is stored, who owns the accounts), Boundary. Test with invented sample data, never real customer records.',
 template=d('''
    # Workflow: {task}

    ## Process map
    Trigger: {trigger}
    Steps today:
    {steps}

    1. [[input]] → [[action]] → [[output]]
    2. [[input]] → [[action]] → [[output]]
    3. [HUMAN] [[input]] → [[the decision a person makes]] → [[output]]
    4. [[input]] → [[action]] → [[output]]

    ## Test run
    Tool: {tool}. Sample data: invented, [[number]] records.
    - Test 1 (normal): [[case]] · expected: [[result]] · actual: [[result]]
    - Test 2 (normal): [[case]] · expected: [[result]] · actual: [[result]]
    - Test 3 (unusual): [[e.g. a message with no address]] · expected: [[result]] · actual: [[result]]

    ## Failure plan
    - If a step fails: [[what happens, e.g. the order stays in the inbox and is flagged]]
    - Who is told: [[person]] by [[how]]

    ## Handoff notes
    - To run it: [[steps]]
    - To stop it: [[steps]]
    - Data stored in: [[where]]; personal data: {data}
    - Accounts owned by: [[the client, in their name]]

    ## Boundary
    - Tested on invented sample data only. A person decides on every [HUMAN] step.
    - [[one more limit, e.g. it never sends messages to customers by itself]]
    '''),
 checks=[BLANKS, H('Process map'), H('Test run'), H('Failure plan'), H('Handoff notes'), H('Boundary'),
         dict(t='lines', match=r'^\d+[.)]\s.*→.*→', min=4, what='mapped steps (input → action → output)'),
         RE(r'\[HUMAN\]', 'Marks at least one human decision', 'Put [HUMAN] on a step where a person must decide.', flags='m'),
         dict(t='lines', match=r'expected\s*:.*actual\s*:', min=3, what='test cases with expected and actual results'),
         RE(r'unusual|edge case', 'Tests an unusual case', 'Add a test for a message or record that breaks the pattern.'),
         RE(r'to stop it', 'Explains how to stop it', 'Add “To stop it: …” to the handoff notes.'),
         dict(t='has', field='task', name='task'), HONEST, dict(t='words', min=180, max=1000)],
 selfcheck=['Could someone who never met you run and stop this workflow from the notes?', 'What happens to the unusual case, and does someone find out?', 'Did any real customer data go into the test?'],
 tips=['Run it by hand three times before automating anything.', 'The unusual case is where automations lose money. Test it first.', 'Accounts and data must belong to the client, never to you.'],
 faq=[('Which automation tool should I learn?', 'Whichever has a free tier that covers the task, but learn the map first. A clear map moves between Zapier, Make, n8n or a spreadsheet in an afternoon.'),
      ('Why mark human steps?', 'Because some decisions (refunds, unusual orders, anything sensitive) should never be automated. Marking them keeps the client in control and keeps you honest about what the tool does.')],
 example_values=dict(task='turning order messages into a delivery list each morning', trigger='a new order message on WhatsApp', data='customer names, addresses, phone numbers'),
 example=EXAMPLE_NOTE + d('''
    # Workflow: turning order messages into a delivery list each morning

    ## Process map
    Trigger: a new order message on WhatsApp
    Steps today: read the message, copy details into a sheet, group by area, send the list to the driver.

    1. Order message → copy name, item, area and time into the order form → a new row in the sheet
    2. New row → a formula looks up the delivery fee for the area → row with fee
    3. [HUMAN] Rows with "special request" → the owner reads and approves or calls the customer → approved rows
    4. Approved rows at 07:30 → a filter view sorted by area → the driver's list, shared as view-only

    ## Test run
    Tool: Google Sheets formulas. Sample data: invented, 12 records.
    - Test 1 (normal): an order in Avondale for 10:00 · expected: fee US$2, in the Avondale group · actual: as expected
    - Test 2 (normal): two orders, same customer · expected: two rows, flagged as same customer · actual: not flagged, fixed with COUNTIF
    - Test 3 (unusual): a message with no area · expected: row marked "ask area" · actual: fee showed #N/A, fixed with IFERROR

    ## Failure plan
    - If a step fails: the row turns red and stays off the driver's list
    - Who is told: the owner, by a red count at the top of the sheet she checks at 07:15

    ## Handoff notes
    - To run it: fill the form for each order; open the "driver" view at 07:30 and share it
    - To stop it: stop using the form; the sheet keeps working as a normal list
    - Data stored in: the owner's Google Drive; personal data: customer names, addresses, phone numbers
    - Accounts owned by: the owner, in her name

    ## Boundary
    - Tested on invented sample data only. A person decides on every [HUMAN] step.
    - It never sends messages to customers by itself.
    '''),
 files={'process-map.csv': 'step,input,action,output,human decides? (yes/no),tool\n', 'test-run.csv': 'test,type (normal/unusual),input,expected,actual,fixed?\n'},
 methods=[21, 24, 25, 30], extra_tools=['ai-workflow-builder', 'zapier-automation', 'google-sheets-script']),

# 10 ---------------------------------------------------------------------------------------------------------------
dict(num=10, slug='weekly-report', track='Reporting & Data', name='Weekly Business Report', emoji='📊',
 h1='Build a weekly business report',
 desc='Free weekly report workshop: choose the few numbers a small business should watch, write the formulas, test them and present one page an owner reads.',
 intro='Owners drown in data and still cannot answer “was this a good week?”. A weekly report picks four or five numbers that drive decisions, calculates them the same way every week and fits on one screen. You will choose the measures, write the formulas, test them against hand counts and design the one-page summary.',
 skills=['Choosing a few measures that lead to decisions', 'Writing formulas that are tested, not trusted', 'Presenting numbers an owner understands in a minute'],
 makes=['Report', 'Formulas', 'QA tests'],
 fields=[F('business', 'Business', 'text', 'e.g. a small grocery shop'),
         F('decisions', 'Which decisions does the owner make each week?', 'textarea', 'What to restock\nWhether to extend opening hours\nWho to pay first', rows=3),
         F('data', 'Where does the data live now?', 'text', 'e.g. a sales notebook copied into a sheet each evening'),
         F('measures', 'Measures you think matter (one per line)', 'textarea', 'Sales per day\nTop 10 items\nCash vs mobile money', rows=4)],
 prompt='Help me design a weekly business report in Markdown for {business}. Weekly decisions:\n{decisions}\nData source: {data}. Candidate measures:\n{measures}\nUse exactly these ## sections: Measures (4 or 5, each: the measure · the decision it informs · the formula), Formulas (spreadsheet formulas with the column names, in code blocks), QA tests (at least 3: a hand count compared with the formula, with the expected result), One-page report (the layout in words: what goes at the top, what is compared with last week), Boundary. Use invented numbers in examples and say they are invented.',
 template=d('''
    # Weekly report: {business}

    ## Measures
    Decisions each week:
    {decisions}

    - [[measure]] · informs: [[decision]] · formula: [[formula]]
    - [[measure]] · informs: [[decision]] · formula: [[formula]]
    - [[measure]] · informs: [[decision]] · formula: [[formula]]
    - [[measure]] · informs: [[decision]] · formula: [[formula]]

    Candidates I dropped, and why: [[which ones did not lead to a decision]]
    {measures}

    ## Formulas
    Data comes from: {data}
    ```
    [[formula 1, e.g. =SUMIFS(C:C, A:A, ">="&B1)]]
    [[formula 2]]
    ```

    ## QA tests
    - Test 1: [[what you count by hand]] · hand count: [[number]] · formula: [[number]] · [[match / fixed]]
    - Test 2: [[test]] · hand count: [[number]] · formula: [[number]] · [[result]]
    - Test 3: [[an empty or odd week]] · hand count: [[number]] · formula: [[number]] · [[result]]

    ## One-page report
    - Top line: [[the one number the owner reads first, compared with last week]]
    - Then: [[the other measures, each with an arrow up or down]]
    - Last: [[one sentence: what to decide this week]]

    ## Boundary
    - Every formula was checked against a hand count. Example numbers are invented.
    - The report shows what happened. It does not predict sales.
    '''),
 checks=[BLANKS, H('Measures'), H('Formulas'), H('QA tests', 'qa tests|quality checks'), H('One-page report'), H('Boundary'),
         dict(t='lines', match=r'informs\s*:.*formula\s*:', min=4, what='measures tied to a decision and a formula'),
         RE(r'^\s*=\w+\(', 'Contains real spreadsheet formulas', 'Write at least one formula that starts with “=” on its own line.'),
         dict(t='lines', match=r'hand count\s*:\s*[\d,.]+', min=3, what='QA tests with a hand count'),
         dict(t='has', field='business', name='business'), HONEST, dict(t='words', min=180, max=1000)],
 selfcheck=['Does every measure lead to a decision the owner actually makes?', 'Did each formula match a hand count, including an odd week?', 'Can the owner read the report in under a minute?'],
 tips=['If nobody would act differently when a number changes, drop it.', 'Test with a week that has a public holiday or a missing day.', 'Always compare with last week. A number alone means little.'],
 faq=[('Which spreadsheet should I use?', 'Any free one: Google Sheets, LibreOffice Calc or Excel online. The formulas here use functions they all share.'),
      ('Should the report forecast next week?', 'Not at first. Report what happened accurately for a month before trying to predict anything, and label any forecast clearly as a guess.')],
 example_values=dict(business='a small grocery shop', data='a sales notebook copied into a sheet each evening'),
 example=EXAMPLE_NOTE + d('''
    # Weekly report: a small grocery shop

    ## Measures
    Decisions each week: what to restock, whether to stay open later on Fridays, which supplier to pay first.

    - Sales this week vs last week · informs: whether the week was normal · formula: SUMIFS on the Amount column by week
    - Top 10 items by quantity · informs: what to restock · formula: a pivot of Item by Quantity, top 10
    - Sales after 18:00 on Friday · informs: whether to stay open later · formula: SUMIFS with a time condition
    - Supplier bills due within 7 days · informs: who to pay first · formula: FILTER on the Bills tab by due date

    Candidates I dropped, and why: "customers per day", because the notebook does not record it.

    ## Formulas
    Data comes from: a sales notebook copied into a sheet each evening
    ```
    =SUMIFS(Sales!C:C, Sales!A:A, ">="&B1, Sales!A:A, "<"&B1+7)
    =SUMIFS(Sales!C:C, Sales!A:A, ">="&B1, Sales!B:B, ">=18:00", Sales!D:D, "Fri")
    =FILTER(Bills!A:C, Bills!C:C <= TODAY()+7)
    ```

    ## QA tests
    - Test 1: sales on Monday 3 November · hand count: 214.50 · formula: 214.50 · match
    - Test 2: bread loaves sold this week · hand count: 96 · formula: 91 · fixed: five rows typed "Bread " with a space
    - Test 3: a week with a public holiday · hand count: 0 for the holiday · formula: 0 · match

    ## One-page report
    - Top line: sales this week, US$1,412, up 6% on last week
    - Then: top 10 items, Friday late sales, bills due, each with an arrow up or down
    - Last: one sentence, e.g. "Restock bread and cooking oil; pay the dairy supplier by Thursday"

    ## Boundary
    - Every formula was checked against a hand count. Example numbers are invented.
    - The report shows what happened. It does not predict sales.
    '''),
 files={'qa-tests.csv': 'test,what was counted by hand,hand count,formula result,match or fix\n', 'measures.csv': 'measure,decision it informs,formula,source column\n'},
 methods=[26, 17], extra_tools=['google-sheets-script']),

# 11 ---------------------------------------------------------------------------------------------------------------
dict(num=11, slug='template-product', track='Digital Product', name='Template Product Kit', emoji='🧩',
 h1='Make a niche template product',
 desc='Free template product workshop: turn a tool you already use into a sellable template with instructions, a clear licence and honest listing copy.',
 intro='A template you already use to solve a problem can help hundreds of people with the same problem. Packaging it well means clean files, instructions a beginner can follow, a licence that says what buyers may do, and listing copy that describes the product honestly. You will plan all four here. Sell it on a free storefront once it is ready.',
 skills=['Turning a personal tool into a product others can use', 'Writing a plain-language licence', 'Writing listing copy that sells without overpromising'],
 makes=['Product files', 'Licence', 'Listing copy'],
 fields=[F('template', 'What is the template?', 'text', 'e.g. a Google Sheets budget for market traders'),
         F('buyer', 'Who is it for, and what problem does it solve?', 'text', 'e.g. traders who mix shop money and home money'),
         F('origin', 'Where did it come from?', 'text', 'e.g. I built it for my aunt’s stall and used it for a year', help='Only sell what you made yourself.'),
         F('price', 'Price idea (with currency)', 'text', 'e.g. US$7')],
 prompt='Help me package a template product in Markdown. Template: {template}. Buyer and problem: {buyer}. Origin: {origin}. Price idea: {price}.\nUse exactly these ## sections: Product files (a numbered list of every file, what it is, and the instructions file with at least 5 steps), Licence (plain language: what buyers may do, may not do, and the refund terms, under 120 words), Listing copy (title under 60 characters, a 2-sentence description, what is included, who it is not for, the price), Proof (origin, validation evidence that others need it, and what is checkable), Boundary. No income claims, no invented reviews or sales numbers.',
 template=d('''
    # Template product: {template}

    ## Product files
    1. [[main file name]] · [[what it is]]
    2. [[instructions file]] · start-here steps:
       - Step 1: [[make a copy]]
       - Step 2: [[step]]
       - Step 3: [[step]]
       - Step 4: [[step]]
       - Step 5: [[step]]
    3. [[example file filled with invented data]]

    ## Licence
    - You may: [[e.g. use it for your own business, change it]]
    - You may not: [[e.g. resell or share the file]]
    - Refunds: [[e.g. within 7 days if it does not open or work as described]]

    ## Listing copy
    Title: [[under 60 characters]]
    Description: [[two sentences: the problem, and what this template does about it]]
    For: {buyer}
    Included: [[the files above, in buyer words]]
    Not for: [[who should not buy it]]
    Price: {price}

    ## Proof
    - Origin: {origin}
    - Validation: [[evidence that others need it, e.g. five people asked for a copy]]
    - [[one checkable fact, e.g. works in Google Sheets and Excel; tested on a phone]]

    ## Boundary
    - No income claims, invented reviews or sales numbers. I made every file myself.
    - [[one more limit, e.g. not financial or tax advice]]
    '''),
 checks=[BLANKS, H('Product files'), H('Licence', 'licen[cs]e'), H('Listing copy'), H('Proof'), H('Boundary'),
         dict(t='lines', match=r'^\s*-\s*step\s*\d', min=5, what='instruction steps'),
         RE(r'validation\s*:', 'Shows validation evidence', 'Add “Validation: …” with evidence that other people need it.'),
         RE(r'you may not\s*:', 'Licence says what buyers may not do', 'Add “You may not: …” to the licence.'),
         RE(r'refunds?\s*:', 'States refund terms', 'Add “Refunds: …”.'),
         RE(r'not for\s*:', 'Says who it is not for', 'Add “Not for: …” to the listing.'),
         RE(r'^title\s*:\s*.{3,60}$', 'Listing title is under 60 characters', 'Shorten the title to 60 characters or fewer.'),
         dict(t='not', re=r'\b(bestsell|best-sell|thousands of (happy )?(buyers|customers)|\d+\+? (sales|happy customers))', flags='i', label='No invented sales or popularity claims', fix='Remove sales numbers and popularity claims you cannot show.'),
         dict(t='has', field='template', name='template'), HONEST, dict(t='words', min=160, max=900)],
 selfcheck=['Could a beginner follow the start-here steps without messaging you?', 'Is every file your own work?', 'Does the listing say who should not buy it?'],
 tips=['Ship an example filled with invented data. People learn the template by seeing it full.', '“Not for” lines reduce refunds and build trust.', 'Price low, gather honest feedback, then improve and raise it.'],
 faq=[('Where can I sell it for free?', 'Storefronts like Whop, Gumroad and Payhip let you list for free and take a fee per sale. Read each fee table before you choose.'),
      ('Can I sell a template I found online?', 'No. Only sell what you made yourself or have written rights to resell. Your licence must match what you actually own.')],
 example_values=dict(template='a Google Sheets budget for market traders', buyer='traders who mix shop money and home money', origin='I built it for my aunt’s stall and used it for a year', price='US$7'),
 example=EXAMPLE_NOTE + d('''
    # Template product: a Google Sheets budget for market traders

    ## Product files
    1. trader-budget.xlsx · the template, with tabs for daily sales, stock, home money and a weekly summary
    2. START-HERE.pdf · start-here steps:
       - Step 1: open the file and choose "Make a copy"
       - Step 2: type your opening cash in the yellow cell
       - Step 3: each evening, enter the day's sales and spending
       - Step 4: move home money in the "home" tab, never from the till
       - Step 5: on Sunday, read the summary tab
    3. trader-budget-example.xlsx · a month filled with invented numbers

    ## Licence
    - You may: use it for your own business and change it however you like
    - You may not: resell, share or upload the file anywhere
    - Refunds: within 7 days if it does not open or work as described

    ## Listing copy
    Title: Market Trader Budget (Google Sheets & Excel)
    Description: Shop money and home money get mixed up, and the week ends without knowing if you made anything. This sheet keeps them apart and shows the answer every Sunday.
    For: traders who mix shop money and home money
    Included: the budget sheet, a filled example and a start-here guide
    Not for: businesses with staff or VAT returns
    Price: US$7

    ## Proof
    - Origin: I built it for my aunt’s stall and used it for a year
    - Validation: six traders on her row asked for a copy; four used it for a month and kept going
    - Works in Google Sheets and Excel; tested on a phone and a laptop

    ## Boundary
    - No income claims, invented reviews or sales numbers. I made every file myself.
    - It is a tracking tool, not financial or tax advice.
    '''),
 files={'licence-template.md': '# Licence\n\n- You may: \n- You may not: \n- Refunds: \n\nPlain language beats legal-sounding language. Say only what you can enforce and what you actually own.\n'},
 methods=[31, 34, 35], extra_tools=['product-description']),

# 12 ---------------------------------------------------------------------------------------------------------------
dict(num=12, slug='micro-tool-test', track='Small AI Tool', name='Micro-tool Validation Plan', emoji='🛠️',
 h1='Validate a one-problem micro-tool',
 desc='Free micro-tool workshop: interview users before writing code, deliver the result by hand first, then plan a small, testable prototype.',
 intro='Most first software products solve a problem nobody pays for. Before you write code, talk to five people with the problem, deliver the result by hand for one of them, and only then plan the smallest tool that does that job. You will log interviews, design the manual prototype and write a test plan with a clear rule for stopping.',
 skills=['Interviewing users about past behaviour', 'Delivering the result manually before automating it', 'Writing a test plan with a stop rule'],
 makes=['Interviews', 'Manual prototype', 'Test plan'],
 fields=[F('idea', 'The micro-tool idea in one line', 'text', 'e.g. a tool that turns a voice note into a printed quotation'),
         F('user', 'Who has the problem?', 'text', 'e.g. plumbers and electricians who quote on site'),
         F('job', 'What do they do today instead?', 'text', 'e.g. write quotes by hand at night, or not at all'),
         F('stack', 'Free tools you would build it with', 'text', 'e.g. a web page, a free AI key, Cloudflare free tier')],
 prompt='Help me validate a micro-tool idea in Markdown. Idea: {idea}. User: {user}. What they do today: {job}. Free stack: {stack}.\nUse exactly these ## sections: Interviews (5 open questions about past behaviour, and a log line per interview: role, date, key quote, pain 1–5), Manual prototype (how I deliver the result by hand for one user, step by step, and what I will measure), Test plan (the smallest tool version, 3 success measures with numbers, a stop rule, and a timebox in days), Data and safety (what data the tool touches and how it is protected), Boundary. Do not invent interview results; leave [[to fill]] where I must record them.',
 template=d('''
    # Micro-tool test: {idea}

    ## Interviews
    For: {user}
    1. Tell me about the last time you had to deal with this: {job}.
    2. [[question about how long it took]]
    3. [[question about what it cost them or what they lost]]
    4. [[question about what they tried]]
    5. [[question about who else is involved]]

    Log (no names):
    - [[role]] · [[date]] · quote: “[[their words]]” · pain: [[1–5]]
    - [[role]] · [[date]] · quote: “[[their words]]” · pain: [[1–5]]

    ## Manual prototype
    For one user, by hand:
    - Step 1: [[how they send you the input]]
    - Step 2: [[what you do]]
    - Step 3: [[what they receive and how fast]]
    - Measure: [[e.g. time saved, whether they use it again next week]]

    ## Test plan
    - Smallest tool: [[the one job it does, nothing else]] · built with {stack}
    - Success measure 1: [[a number]]
    - Success measure 2: [[a number]]
    - Success measure 3: [[a number]]
    - Stop rule: [[e.g. if fewer than 3 of 5 users use it twice, stop or change the idea]]
    - Timebox: [[number]] days

    ## Data and safety
    [[what data it touches, where it is stored, who can see it]]

    ## Boundary
    - Interview results are real and recorded without names. No invented users or demand.
    - [[one more limit, e.g. it drafts quotes; a person checks every price]]
    '''),
 checks=[BLANKS, H('Interviews'), H('Manual prototype'), H('Test plan'), H('Data and safety'), H('Boundary'),
         dict(t='lines', match=r'^\d+[.)]\s', min=5, what='interview questions'),
         dict(t='lines', match=r'pain\s*:\s*[1-5]', min=2, what='interview log lines with a pain score'),
         RE(r'stop rule\s*:.*\d', 'Has a stop rule with a number', 'Write a stop rule with a number, e.g. “fewer than 3 of 5 users”.'),
         RE(r'timebox\s*:\s*\d+', 'Has a timebox in days', 'Write “Timebox: 14 days”.'),
         dict(t='has', field='idea', name='idea'), HONEST, dict(t='words', min=180, max=1000)],
 selfcheck=['Did the interviews ask about what people did, not what they would buy?', 'Did someone use the manual version more than once?', 'Would you really stop if the stop rule is triggered?'],
 tips=['Doing it by hand is slow on purpose. It shows you what the tool really needs.', 'Write the stop rule before you start. It is much harder afterwards.', 'The smallest tool does one job well. Add nothing until that job is used.'],
 faq=[('Why not just build it and see?', 'Because building is the most expensive way to learn that nobody wants it. Interviews and a manual version cost days, not months.'),
      ('Can I build it for free?', 'Usually yes: a static page, the learner’s own free AI key and a free hosting tier cover most micro-tools. The Open Practice builders can generate the first version.')],
 example_values=dict(idea='a tool that turns a voice note into a printed quotation', user='plumbers and electricians who quote on site', job='write quotes by hand at night', stack='a web page, a free AI key, Cloudflare free tier'),
 example=EXAMPLE_NOTE + d('''
    # Micro-tool test: a tool that turns a voice note into a printed quotation

    ## Interviews
    For: plumbers and electricians who quote on site
    1. Tell me about the last time you had to deal with this: write quotes by hand at night.
    2. How long did that quote take, from the site visit to sending it?
    3. Have you ever lost a job because the quote arrived late?
    4. What have you tried: templates, an app, asking someone else?
    5. Who else sees the quote before the customer does?

    Log (no names):
    - plumber · 6 November · quote: “I lose about one job a week because the quote is late” · pain: 5
    - electrician · 7 November · quote: “My daughter types them on Sundays” · pain: 4
    - plumber · 7 November · quote: “Customers just want a number on WhatsApp” · pain: 2

    ## Manual prototype
    For one user, by hand:
    - Step 1: he sends a voice note after the site visit
    - Step 2: I type the items and prices into a quote template and check the maths
    - Step 3: he receives a PDF on WhatsApp within 2 hours
    - Measure: whether he sends me a second voice note within a week, and hours saved per quote

    ## Test plan
    - Smallest tool: voice note in, draft quote out, nothing else · built with a web page, a free AI key, Cloudflare free tier
    - Success measure 1: 3 of 5 tradespeople use it at least twice in two weeks
    - Success measure 2: a quote takes under 10 minutes from voice note to PDF
    - Success measure 3: no price errors in 10 checked quotes
    - Stop rule: if fewer than 3 of 5 use it twice, stop or change the idea
    - Timebox: 14 days

    ## Data and safety
    Voice notes and quotes contain customer addresses. They are deleted after 30 days and never used to train anything.

    ## Boundary
    - Interview results are real and recorded without names. No invented users or demand.
    - It drafts quotes; a person checks every price before sending.
    '''),
 files={'interview-log.csv': 'date,role (no names),key quote (their words),pain 1-5,what they do today,would try the manual version?\n', 'test-plan.csv': 'measure,target number,actual,met?\n'},
 methods=[39, 40, 32], extra_tools=['pwa-app-creator', 'chrome-extension-creator', 'telegram-bot-creator']),
]

BY_SLUG = {b['slug']: b for b in BUILDS}
assert len(BUILDS) == 12 and len(BY_SLUG) == 12 and [b['num'] for b in BUILDS] == list(range(1, 13))
