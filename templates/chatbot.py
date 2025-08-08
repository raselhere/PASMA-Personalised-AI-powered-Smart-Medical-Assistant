import re

# Disclaimer to add to medical advice
MEDICAL_DISCLAIMER = "Note: This information is for educational purposes only and not a substitute for professional medical advice. Always consult with a healthcare provider for medical concerns."

# Health-related responses organized by categories
responses = {
    # General Wellness
    "how to stay healthy": f"Maintaining good health involves regular exercise, balanced nutrition, adequate sleep, stress management, and regular check-ups. {MEDICAL_DISCLAIMER}",
    "tips for good health": "For good health: eat a balanced diet, exercise regularly, get enough sleep, manage stress, stay hydrated, and avoid smoking and excessive alcohol. Regular check-ups are also important.",
    "how to boost immune system": "To boost your immune system: eat nutrient-rich foods, get adequate sleep, exercise regularly, manage stress, stay hydrated, and consider vitamin D supplementation if deficient.",
    "how to improve overall health": "Improve overall health through regular physical activity, balanced nutrition, adequate sleep (7-9 hours), stress management, staying hydrated, and avoiding tobacco and excessive alcohol.",
    "preventive health measures": "Preventive health measures include regular check-ups, vaccinations, cancer screenings, maintaining healthy weight, regular exercise, and avoiding smoking and excessive alcohol.",

    # Common Symptoms
    "headache causes": f"Headaches can be caused by stress, dehydration, lack of sleep, eye strain, sinus issues, or more serious conditions. Persistent or severe headaches warrant medical attention. {MEDICAL_DISCLAIMER}",
    "fever treatment": "For fever: rest, stay hydrated, take acetaminophen or ibuprofen if needed (follow dosage instructions), and use light clothing/blankets. Seek medical help for high fevers (above 103°F/39.4°C) or if it persists.",
    "sore throat remedies": "Sore throat remedies include warm saltwater gargles, staying hydrated, throat lozenges, honey in warm tea, and OTC pain relievers. See a doctor if it persists beyond a week or is severe.",
    "cough treatment": "For coughs: stay hydrated, use honey (if over 1 year old), try cough drops, use a humidifier, and avoid irritants. See a doctor for persistent coughs or if accompanied by other concerning symptoms.",
    "stomach pain causes": "Stomach pain can result from indigestion, gas, constipation, food poisoning, ulcers, or more serious conditions. Seek medical attention for severe or persistent pain, especially with fever or vomiting.",
    "nausea remedies": "For nausea: try ginger tea, small bland meals, avoid strong odors, stay hydrated, and rest. Seek medical help if nausea persists or is accompanied by severe pain or dehydration.",
    "dizziness causes": "Dizziness may be caused by dehydration, inner ear issues, low blood sugar, anemia, or medication side effects. Consult a doctor if dizziness is severe, persistent, or accompanied by other symptoms.",
    "back pain relief": "For back pain relief: apply ice/heat, take OTC pain relievers, maintain good posture, try gentle stretching, and avoid heavy lifting. See a doctor for severe or persistent pain, especially with numbness.",
    "joint pain causes": "Joint pain can be caused by injury, arthritis, overuse, infection, or autoimmune conditions. Rest, ice, compression, and elevation (RICE) may help. Consult a doctor for persistent or severe pain.",
    "fatigue reasons": "Fatigue can result from poor sleep, stress, anemia, thyroid issues, depression, or various medical conditions. Improve sleep habits and see a doctor if fatigue is persistent or severe.",

    # Nutrition and Diet
    "healthy diet tips": "A healthy diet includes plenty of fruits, vegetables, whole grains, lean proteins, and healthy fats. Limit processed foods, added sugars, and excessive salt. Stay hydrated with water.",
    "balanced meal plan": "A balanced meal should include: 1/2 plate vegetables/fruits, 1/4 plate whole grains, and 1/4 plate protein. Include healthy fats and dairy/alternatives in moderation.",
    "how much water to drink": "Most adults should drink about 8 cups (64 ounces) of water daily, but needs vary based on activity level, climate, and individual health. Urine should be pale yellow if properly hydrated.",
    "best foods for energy": "For energy, eat complex carbohydrates (whole grains, legumes), lean proteins, nuts, seeds, and fruits. Include iron-rich foods like leafy greens and avoid excessive sugar which causes energy crashes.",
    "foods to avoid": "Limit or avoid ultra-processed foods, foods with added sugars, trans fats, excessive sodium, and alcohol. These can contribute to various health problems when consumed regularly.",
    "protein sources": "Good protein sources include lean meats, poultry, fish, eggs, dairy, legumes (beans, lentils), tofu, tempeh, nuts, and seeds. Plant proteins are beneficial for overall health.",
    "healthy snack ideas": "Healthy snacks include fruit with nut butter, Greek yogurt with berries, hummus with vegetables, a small handful of nuts, or whole grain crackers with cheese.",
    "vitamins and minerals": "Essential vitamins and minerals come from a varied diet. Fruits, vegetables, whole grains, lean proteins, and healthy fats provide most nutrients needed for good health.",
    "weight loss tips": "For healthy weight loss: create a modest calorie deficit, focus on nutrient-dense foods, increase physical activity, get adequate sleep, manage stress, and make sustainable lifestyle changes.",
    "intermittent fasting": "Intermittent fasting involves cycling between eating and fasting periods. Common methods include 16:8 or 5:2. It may help with weight management but isn't suitable for everyone.",

    # Exercise and Fitness
    "exercise benefits": "Regular exercise improves cardiovascular health, strengthens muscles and bones, enhances mental health, helps maintain healthy weight, improves sleep, and reduces risk of many diseases.",
    "how much exercise needed": "Adults should aim for at least 150 minutes of moderate aerobic activity or 75 minutes of vigorous activity weekly, plus muscle-strengthening activities twice weekly.",
    "best exercises for beginners": "Beginners should start with walking, swimming, cycling, or basic bodyweight exercises like modified push-ups, squats, and lunges. Start slowly and gradually increase intensity.",
    "cardio vs strength training": "Both cardio and strength training are important. Cardio improves heart health and burns calories, while strength training builds muscle, increases metabolism, and strengthens bones.",
    "exercise without gym": "Home exercises include walking, jogging, bodyweight exercises (push-ups, squats, lunges), jumping jacks, stair climbing, and online workout videos. Resistance bands are affordable equipment options.",
    "stretching importance": "Stretching improves flexibility, range of motion, posture, and blood flow to muscles. It can reduce injury risk and muscle tension. Hold stretches for 15-30 seconds without bouncing.",
    "overtraining symptoms": "Overtraining signs include persistent fatigue, decreased performance, increased resting heart rate, frequent injuries, mood changes, and disrupted sleep. Rest and recovery are essential.",
    "best time to exercise": "The best time to exercise is when you can consistently do it. Morning exercise may boost metabolism and improve sleep, but afternoon workouts often have performance advantages.",
    "exercise for weight loss": "For weight loss, combine cardio (walking, running, cycling) with strength training. Aim for at least 30 minutes most days, and include high-intensity intervals for efficiency.",
    "how to stay motivated": "Stay motivated by setting specific goals, finding activities you enjoy, exercising with friends, tracking progress, rewarding yourself, and mixing up your routine to prevent boredom.",

    # Mental Health
    "stress management": "Manage stress through regular exercise, adequate sleep, deep breathing, meditation, time in nature, limiting caffeine and alcohol, and connecting with supportive people.",
    "anxiety relief": "For anxiety relief: practice deep breathing, progressive muscle relaxation, mindfulness meditation, regular exercise, limit caffeine, maintain a consistent sleep schedule, and consider counseling.",
    "depression symptoms": "Depression symptoms include persistent sadness, loss of interest in activities, changes in appetite or sleep, fatigue, difficulty concentrating, feelings of worthlessness, and thoughts of death.",
    "improve mental health": "Improve mental health through regular physical activity, adequate sleep, healthy nutrition, stress management, social connections, mindfulness practices, and limiting alcohol and screen time.",
    "mindfulness techniques": "Mindfulness techniques include focused breathing, body scan meditation, mindful eating, walking meditation, and simply paying full attention to everyday activities without judgment.",
    "signs of burnout": "Burnout signs include extreme exhaustion, cynicism, detachment, reduced performance, and physical symptoms like headaches or stomach problems. Address it by setting boundaries and seeking support.",
    "how to sleep better": "For better sleep: maintain a consistent schedule, create a relaxing bedtime routine, keep your bedroom cool and dark, limit screen time before bed, avoid caffeine and alcohol near bedtime.",
    "social connection importance": "Social connections boost mental health, increase longevity, strengthen immunity, and reduce stress. Quality relationships matter more than quantity.",
    "grief coping strategies": "Cope with grief by acknowledging your feelings, seeking support from others, taking care of physical needs, being patient with the process, and considering professional help if needed.",
    "work-life balance": "Improve work-life balance by setting boundaries, prioritizing tasks, scheduling personal time, learning to say no, using vacation time, and disconnecting from work during off hours.",

    # Sleep
    "sleep importance": "Sleep is essential for memory consolidation, immune function, tissue repair, hormone regulation, and emotional well-being. Most adults need 7-9 hours nightly.",
    "insomnia remedies": "For insomnia: maintain a regular sleep schedule, create a relaxing bedtime routine, limit screen time before bed, ensure your bedroom is dark and cool, and avoid caffeine and alcohol near bedtime.",
    "sleep apnea symptoms": "Sleep apnea symptoms include loud snoring, gasping for air during sleep, morning headaches, excessive daytime sleepiness, difficulty concentrating, and irritability. Medical evaluation is important.",
    "napping benefits": "Short naps (20-30 minutes) can boost alertness, mood, and performance without interfering with nighttime sleep. Longer naps may cause sleep inertia or disrupt nighttime sleep.",
    "sleep hygiene tips": "Good sleep hygiene includes consistent sleep-wake times, a comfortable sleep environment, limiting caffeine and alcohol, regular exercise (not too close to bedtime), and a relaxing pre-sleep routine.",
    "jet lag management": "Manage jet lag by gradually adjusting your schedule before travel, staying hydrated, getting sunlight at the right times in your new location, and considering melatonin after consulting a doctor.",
    "sleep and weight": "Poor sleep can contribute to weight gain by affecting hunger hormones, increasing cravings, reducing energy for physical activity, and altering metabolism. Aim for 7-9 hours nightly.",
    "children sleep needs": "Children's sleep needs vary by age: newborns (14-17 hours), infants (12-15 hours), toddlers (11-14 hours), preschoolers (10-13 hours), school-age (9-11 hours), and teens (8-10 hours).",
    "sleep tracking": "Sleep tracking can provide insights into sleep patterns but has limitations. Focus on how you feel during the day rather than obsessing over data. Consistent sleep habits matter most.",
    "shift work sleep disorder": "For shift workers: use blackout curtains, white noise, consistent sleep schedule when possible, strategic napping, light therapy, and limit caffeine. Consult a doctor if experiencing significant issues.",

    # First Aid
    "basic first aid kit": "A basic first aid kit should include: adhesive bandages, gauze, adhesive tape, antiseptic wipes, antibiotic ointment, tweezers, scissors, disposable gloves, and emergency contact information.",
    "cuts and scrapes treatment": "For cuts and scrapes: clean with soap and water, apply antibiotic ointment, cover with a sterile bandage, and change dressing daily. Seek medical help for deep, large, or heavily bleeding wounds.",
    "burn treatment": "For minor burns: cool with running water for 10-15 minutes, don't use ice, apply aloe vera or moisturizer, take OTC pain relievers if needed. Seek medical help for large or deep burns.",
    "sprain treatment": "For sprains: follow RICE - Rest the area, Ice for 20 minutes several times daily, Compress with a bandage, and Elevate above heart level. See a doctor if you can't bear weight or have severe pain.",
    "choking first aid": "For choking: if the person can cough, let them. If they can't cough, speak or breathe, give 5 back blows between shoulder blades, then 5 abdominal thrusts (Heimlich maneuver). Call emergency services.",
    "heart attack signs": "Heart attack signs include chest pain/pressure, pain radiating to arm/jaw/back, shortness of breath, cold sweat, nausea, and lightheadedness. Call emergency services immediately if suspected.",
    "stroke symptoms": "Remember FAST for stroke: Face drooping, Arm weakness, Speech difficulty, Time to call emergency services. Other symptoms include sudden numbness, confusion, trouble seeing, dizziness, or severe headache.",
    "heat exhaustion treatment": "For heat exhaustion: move to a cool place, remove excess clothing, sip water, take a cool shower/bath or use cold compresses. Seek medical help if symptoms worsen or don't improve within an hour.",
    "hypothermia signs": "Hypothermia signs include shivering, confusion, slurred speech, drowsiness, and weak pulse. Remove wet clothing, warm the person with dry blankets, and seek emergency medical help immediately.",
    "insect bite treatment": "For insect bites: wash with soap and water, apply cold compress to reduce swelling, use OTC antihistamines or hydrocortisone cream for itching. Seek medical help for severe reactions.",

    # Medications
    "over the counter pain relievers": "Common OTC pain relievers include acetaminophen (Tylenol) and NSAIDs like ibuprofen (Advil, Motrin) and naproxen (Aleve). Each works differently and has different side effect profiles.",
    "antibiotic use": "Antibiotics only work for bacterial infections, not viruses like colds or flu. Always complete the full course as prescribed, even if you feel better. Misuse contributes to antibiotic resistance.",
    "medication side effects": "All medications can have side effects. Common ones include nausea, dizziness, fatigue, and headaches. Report severe or persistent side effects to your healthcare provider immediately.",
    "drug interactions": "Drug interactions can occur between medications, supplements, foods, and alcohol. Always inform your healthcare provider about all substances you take and read medication labels carefully.",
    "storing medications": "Store medications in a cool, dry place away from direct sunlight and out of reach of children. Some require refrigeration. Don't use expired medications and dispose of them properly.",
    "generic vs brand medications": "Generic medications contain the same active ingredients as brand-name versions and are equally effective but typically cost less. They must meet the same FDA standards for quality and safety.",
    "taking antibiotics": "Take antibiotics exactly as prescribed, at regular intervals, and complete the full course. Some should be taken with food, others on an empty stomach. Don't share antibiotics or save for later use.",
    "pain medication types": "Pain medications include acetaminophen (reduces pain signals), NSAIDs (reduce inflammation), and opioids (block pain signals). Each has different uses, risks, and side effects.",
    "medication allergies": "Medication allergy symptoms include rash, hives, itching, swelling, wheezing, and anaphylaxis. Seek immediate medical attention for severe reactions and always report allergies to healthcare providers.",
    "supplements safety": "Dietary supplements aren't regulated like medications. Discuss with your healthcare provider before taking them, especially if you take prescription medications or have health conditions.",

    # Chronic Conditions
    "diabetes management": "Diabetes management includes monitoring blood sugar, taking medications as prescribed, following a healthy diet, regular physical activity, stress management, and regular check-ups with healthcare providers.",
    "hypertension control": "Control hypertension through regular exercise, DASH diet (low sodium, high in fruits/vegetables), limiting alcohol, maintaining healthy weight, not smoking, managing stress, and taking prescribed medications.",
    "asthma triggers": "Common asthma triggers include allergens (pollen, dust mites, pet dander), respiratory infections, exercise, cold air, smoke, pollution, and certain medications. Identify and avoid your specific triggers.",
    "arthritis pain management": "Manage arthritis pain through regular gentle exercise, maintaining healthy weight, hot/cold therapy, medications as prescribed, assistive devices, and joint protection techniques.",
    "heart disease prevention": "Prevent heart disease by not smoking, exercising regularly, eating a heart-healthy diet, maintaining healthy weight and cholesterol levels, managing stress, and controlling conditions like diabetes and hypertension.",
    "migraine prevention": "Prevent migraines by identifying and avoiding triggers, maintaining regular sleep and meal schedules, managing stress, staying hydrated, exercising regularly, and taking preventive medications if prescribed.",
    "copd management": "COPD management includes smoking cessation, medications as prescribed, pulmonary rehabilitation, oxygen therapy if needed, regular vaccinations, and avoiding respiratory irritants and infections.",
    "ibs relief": "For IBS relief: identify and avoid trigger foods, eat smaller regular meals, stay hydrated, exercise regularly, manage stress, and consider fiber supplements or probiotics after consulting your doctor.",
    "autoimmune disease basics": "Autoimmune diseases occur when the immune system attacks healthy cells. Management typically involves medications to reduce immune response, lifestyle modifications, and regular monitoring.",
    "chronic pain coping": "Cope with chronic pain through multimodal approaches: appropriate medications, physical therapy, exercise, stress management techniques, cognitive behavioral therapy, and support groups.",

    # Women's Health
    "menstrual pain relief": "For menstrual pain: use heat therapy, take OTC pain relievers, exercise regularly, try relaxation techniques, and consider hormonal birth control if pain is severe. Consult a doctor for persistent severe pain.",
    "pregnancy early signs": "Early pregnancy signs include missed period, fatigue, breast tenderness, nausea/vomiting, frequent urination, and mood changes. Take a pregnancy test and consult a healthcare provider if pregnancy is suspected.",
    "menopause symptoms": "Menopause symptoms include hot flashes, night sweats, sleep disturbances, mood changes, vaginal dryness, and irregular periods. Management options include lifestyle changes and medical treatments.",
    "breast self-exam": "For breast self-exams: check monthly after your period, look for visual changes, feel for lumps in circular patterns, and report any changes to your doctor. Clinical exams and mammograms are also important.",
    "birth control options": "Birth control options include hormonal methods (pills, patches, rings, injections), barrier methods (condoms, diaphragms), IUDs, implants, and permanent methods. Effectiveness and side effects vary.",
    "urinary tract infection": "UTI symptoms include frequent/urgent urination, burning sensation, cloudy/strong-smelling urine, and pelvic pain. Drink plenty of water, urinate after sex, and see a doctor for antibiotics if needed.",
    "pap smear importance": "Pap smears screen for cervical cancer by detecting abnormal cells. Most women ages 21-65 should have them every 3-5 years depending on age and history. They're essential for early detection.",
    "pregnancy nutrition": "During pregnancy: eat a variety of nutrient-rich foods, take prenatal vitamins, increase calorie intake moderately, stay hydrated, avoid alcohol/raw foods/excessive caffeine, and consult your healthcare provider.",
    "breastfeeding tips": "For successful breastfeeding: start within an hour of birth, ensure proper latch, feed on demand (8-12 times daily), stay hydrated, eat nutritious foods, and seek help from lactation consultants if needed.",
    "osteoporosis prevention": "Prevent osteoporosis through adequate calcium and vitamin D intake, weight-bearing and resistance exercises, not smoking, limiting alcohol, and bone density testing as recommended.",

    # Men's Health
    "prostate health": "For prostate health: eat a balanced diet rich in fruits and vegetables, exercise regularly, maintain healthy weight, limit alcohol, don't smoke, and get regular check-ups including PSA tests as recommended.",
    "testicular self-exam": "Perform testicular self-exams monthly: check each testicle separately using both hands, rolling it between fingers to feel for lumps or changes. Report any abnormalities to your doctor promptly.",
    "erectile dysfunction": "Erectile dysfunction can result from physical causes (cardiovascular issues, diabetes, obesity) or psychological factors. Treatments include lifestyle changes, medications, devices, or therapy.",
    "male pattern baldness": "Male pattern baldness is primarily genetic. Treatments include medications like minoxidil and finasteride, hair transplantation, laser therapy, or embracing hair loss with confidence.",
    "low testosterone": "Low testosterone symptoms include fatigue, reduced libido, erectile dysfunction, depression, and decreased muscle mass. Diagnosis requires blood tests. Treatments include lifestyle changes and testosterone replacement.",
    "prostate cancer screening": "Prostate cancer screening typically involves PSA blood tests and digital rectal exams. Discuss with your doctor about when to start screening based on your age and risk factors.",
    "men's mental health": "Men often face barriers to seeking mental health support. Depression and anxiety are common but treatable. Exercise, social connection, therapy, and sometimes medication can help.",
    "heart attack risk men": "Men's heart attack risk increases with age, family history, smoking, high blood pressure/cholesterol, diabetes, obesity, stress, and sedentary lifestyle. Regular check-ups and lifestyle modifications are essential.",
    "male fertility": "Factors affecting male fertility include age, smoking, alcohol, certain medications, obesity, stress, and environmental toxins. Healthy lifestyle, regular exercise, and avoiding excessive heat to testicles can help.",
    "men's nutrition needs": "Men typically need more calories than women and adequate protein for muscle maintenance. Focus on fruits, vegetables, whole grains, lean proteins, and healthy fats. Limit processed foods and alcohol.",

    # Children's Health
    "childhood vaccinations": "Childhood vaccinations protect against serious diseases and are carefully tested for safety. Follow the recommended schedule from your pediatrician for optimal protection.",
    "fever in children": "For children's fever: use acetaminophen or ibuprofen (not aspirin) as directed, dress lightly, ensure adequate fluids, and rest. Contact a doctor for high fevers, infants under 3 months, or concerning symptoms.",
    "child development milestones": "Major milestones include: sitting (6 months), crawling (9 months), walking (12-15 months), first words (12 months), and speaking in sentences (24 months). Development varies among children.",
    "healthy snacks for kids": "Healthy kids' snacks include fresh fruits, vegetables with dip, yogurt, cheese, whole grain crackers, and nut butters (if no allergies). Limit processed foods, added sugars, and salt.",
    "childhood obesity prevention": "Prevent childhood obesity through balanced nutrition, limited screen time, regular physical activity, adequate sleep, family meals, and being a positive role model for healthy behaviors.",
    "common childhood illnesses": "Common childhood illnesses include colds, ear infections, strep throat, and gastroenteritis. Good hygiene, adequate nutrition, sleep, and vaccinations help prevent many illnesses.",
    "screen time for children": "Recommended limits: no screen time under 18-24 months (except video chatting), 1 hour/day of quality programming for ages 2-5, and consistent limits with media-free times for older children.",
    "child sleep problems": "Address children's sleep problems with consistent bedtime routines, regular sleep schedule, comfortable sleep environment, limited screen time before bed, and addressing fears or anxieties.",
    "adhd symptoms": "ADHD symptoms include difficulty sustaining attention, hyperactivity, impulsivity, disorganization, and forgetfulness that interfere with functioning. Proper evaluation by healthcare professionals is essential.",
    "food allergies in children": "Common food allergens include milk, eggs, peanuts, tree nuts, soy, wheat, fish, and shellfish. Symptoms range from mild to severe. Seek immediate medical help for severe reactions.",

    # Senior Health
    "healthy aging tips": "For healthy aging: stay physically active, eat nutritious foods, maintain social connections, challenge your brain, get regular check-ups, don't smoke, limit alcohol, and manage chronic conditions.",
    "fall prevention": "Prevent falls by removing home hazards, using assistive devices if needed, wearing proper footwear, staying physically active, having vision checked regularly, and reviewing medications that might cause dizziness.",
    "memory improvement": "Improve memory through mental stimulation, physical exercise, proper nutrition, adequate sleep, stress management, social engagement, and treating underlying health conditions.",
    "arthritis management": "Manage arthritis with regular gentle exercise, maintaining healthy weight, hot/cold therapy, assistive devices, medications as prescribed, and joint protection techniques.",
    "senior nutrition": "Seniors need nutrient-dense foods with adequate protein, calcium, vitamin D, B12, and fiber. Stay hydrated, limit sodium and added sugars, and adjust calorie intake as metabolism slows.",
    "medication management for elderly": "Help seniors manage medications by using pill organizers, setting reminders, maintaining an updated medication list, reviewing regularly with healthcare providers, and watching for side effects.",
    "hearing loss signs": "Signs of hearing loss include turning up volume, asking people to repeat themselves, difficulty understanding conversation in noisy environments, and withdrawing from social situations.",
    "vision changes with age": "Age-related vision changes include presbyopia (difficulty focusing up close), increased need for light, difficulty distinguishing colors, and potentially cataracts, glaucoma, or macular degeneration.",
    "elder care options": "Elder care options include aging in place with support services, independent living communities, assisted living, nursing homes, and continuing care retirement communities. Consider needs, preferences, and finances.",
    "advance care planning": "Advance care planning involves documenting healthcare wishes through advance directives, including living wills and healthcare proxies. Discuss preferences with family and healthcare providers.",

    # Preventive Care
    "health screenings by age": "Important screenings include blood pressure (all adults), cholesterol (adults 20+), colorectal cancer (45-75), breast cancer (women 40+), cervical cancer (women 21-65), and bone density (women 65+).",
    "vaccination schedule adults": "Adult vaccines include annual flu shots, Td/Tdap boosters every 10 years, shingles vaccine (50+), pneumococcal vaccines (65+), and others based on health conditions, occupation, and travel.",
    "dental health tips": "Maintain dental health by brushing twice daily with fluoride toothpaste, flossing daily, limiting sugary foods/drinks, not smoking, and having regular dental check-ups and cleanings.",
    "eye exam frequency": "Adults should have comprehensive eye exams every 1-2 years, more frequently with age or conditions like diabetes. Children need screening at birth, 6 months, 3 years, and before starting school.",
    "skin cancer prevention": "Prevent skin cancer by using broad-spectrum sunscreen (SPF 30+), wearing protective clothing, seeking shade, avoiding tanning beds, and checking skin regularly for changing moles.",
    "blood pressure checks": "Have blood pressure checked at least every 2 years if normal (less than 120/80), or more frequently if elevated. Home monitoring may be beneficial for some people.",
    "cholesterol screening": "Adults should have cholesterol checked every 4-6 years starting at age 20, or more frequently with risk factors. Testing includes total, HDL, LDL cholesterol, and triglycerides.",
    "diabetes screening": "Diabetes screening is recommended for adults 45+ or earlier with risk factors like obesity, family history, or high blood pressure. Screening typically involves fasting blood glucose or A1C tests.",
    "bone density testing": "Bone density testing is recommended for women 65+ and men 70+, or earlier with risk factors for osteoporosis. Results help determine fracture risk and need for intervention.",
    "cancer warning signs": "Cancer warning signs include unexplained weight loss, persistent pain, unusual bleeding/discharge, thickening/lump, difficulty swallowing, changes in warts/moles, persistent cough, and changes in bowel/bladder habits.",

    # Infectious Diseases
    "cold vs flu": "Colds typically develop gradually with mild symptoms, while flu comes on suddenly with more severe symptoms including fever, body aches, and extreme fatigue. Both are viral but flu can be more serious.",
    "covid 19 symptoms": "COVID-19 symptoms include fever, cough, shortness of breath, fatigue, body aches, headache, loss of taste/smell, sore throat, congestion, nausea, and diarrhea. Severity ranges from mild to severe.",
    "preventing infections": "Prevent infections by washing hands frequently, avoiding close contact with sick people, staying up to date on vaccinations, preparing food safely, using insect repellent when needed, and practicing safe sex.",
    "when to take antibiotics": "Take antibiotics only for bacterial infections (not viruses like colds or flu), exactly as prescribed, completing the full course even if you feel better. Misuse contributes to antibiotic resistance.",
    "food poisoning": "Food poisoning symptoms include nausea, vomiting, diarrhea, abdominal pain, and fever. Most cases resolve with rest and hydration. Seek medical help for severe symptoms or high-risk individuals.",
    "common stds": "Common STDs include chlamydia, gonorrhea, syphilis, herpes, HPV, and HIV. Many have no symptoms initially. Prevention includes safe sex practices and regular testing if sexually active.",
    "seasonal allergies vs cold": "Allergies typically cause itchy eyes/nose/throat, clear runny nose, and sneezing without fever, while colds often include cough, sore throat, thicker nasal discharge, and sometimes fever.",
    "pneumonia symptoms": "Pneumonia symptoms include cough with phlegm, fever, chills, shortness of breath, chest pain, fatigue, and sometimes confusion (especially in older adults). Seek medical attention if suspected.",
    "mono symptoms": "Mononucleosis symptoms include extreme fatigue, sore throat, fever, swollen lymph nodes, and sometimes swollen spleen. Rest and fluids are important; symptoms may last several weeks.",
    "lyme disease": "Lyme disease often begins with a bull's-eye rash and may progress to fever, fatigue, joint pain, and neurological problems if untreated. Prevention includes avoiding tick-infested areas and using repellent.",

    # Travel Health
    "travel vaccinations": "Travel vaccinations depend on destination, activities, and health status. Common ones include hepatitis A/B, typhoid, yellow fever, and meningitis. Consult a travel medicine specialist 4-6 weeks before travel.",
    "preventing travelers diarrhea": "Prevent traveler's diarrhea by drinking bottled/purified water, avoiding ice, raw fruits/vegetables unless peeled, undercooked foods, and street food. Wash hands frequently.",
    "jet lag management": "Manage jet lag by gradually adjusting to new time zone before travel, staying hydrated, getting sunlight at appropriate times, avoiding alcohol/caffeine during travel, and considering melatonin after consulting with your doctor.",
    "altitude sickness": "Prevent altitude sickness by ascending gradually, staying hydrated, avoiding alcohol, eating carbohydrates, and considering medications like acetazolamide. Descend if symptoms become severe.",
    "travel health kit": "A travel health kit should include: prescription medications, first aid supplies, OTC pain relievers, anti-diarrheal medication, motion sickness remedies, insect repellent, sunscreen, and hand sanitizer.",
    "safe food while traveling": "For safe food while traveling: eat thoroughly cooked, hot foods, avoid raw foods unless peelable, drink bottled/purified water, avoid ice, and eat at reputable establishments.",
    "malaria prevention": "Prevent malaria through antimalarial medications (started before travel), using insect repellent, wearing long sleeves/pants, sleeping under treated bed nets, and staying in screened/air-conditioned rooms.",
    "travel with chronic conditions": "When traveling with chronic conditions: bring extra medication, carry a doctor's note, wear medical alert bracelet if relevant, research medical facilities at destination, and consider travel insurance.",
    "travel during pregnancy": "For pregnancy travel: consult your doctor first, avoid high-risk destinations, stay hydrated, move frequently during long trips, wear support stockings, and know healthcare options at your destination.",
    "travel insurance importance": "Travel insurance can cover medical emergencies, trip cancellation/interruption, lost luggage, and evacuation. It's especially important for international travel or those with health conditions.",

    # Miscellaneous Health Topics
    "quitting smoking": "Quit smoking by using nicotine replacement therapy, prescription medications, behavioral therapy, support groups, and lifestyle changes. Benefits begin within hours and increase over time.",
    "alcohol health effects": "Alcohol affects nearly every organ system. Moderate consumption (up to 1 drink daily for women, 2 for men) may have some cardiovascular benefits, but heavier drinking increases risks of liver disease, heart problems, cancer, and accidents.",
    "vaping risks": "Vaping risks include lung injury, nicotine addiction, exposure to harmful chemicals, and potential gateway to cigarette smoking. Long-term effects are still being studied. It's particularly harmful for youth and non-smokers.",
    "blue light effects": "Blue light from screens can disrupt sleep by suppressing melatonin production. Consider using night mode on devices, blue light filtering glasses, or avoiding screens 1-2 hours before bedtime.",
    "caffeine effects": "Caffeine temporarily increases alertness but can cause jitteriness, increased heart rate, anxiety, and sleep disturbances in some people. Most adults can safely consume up to 400mg daily (about 4 cups of coffee).",
    "sugar health impact": "Excessive sugar consumption is linked to obesity, type 2 diabetes, heart disease, fatty liver disease, tooth decay, and possibly certain cancers. The WHO recommends limiting added sugars to less than 10% of daily calories.",
    "sitting health risks": "Prolonged sitting increases risks of obesity, heart disease, diabetes, cancer, and early death, even with regular exercise. Break up sitting time with movement every 30 minutes and consider a standing desk.",
    "hydration importance": "Proper hydration supports digestion, circulation, temperature regulation, joint lubrication, and waste removal. Needs vary by individual, but urine should be pale yellow. Increase intake during exercise and hot weather.",
    "organic food benefits": "Organic foods may contain fewer pesticide residues and antibiotic-resistant bacteria. Environmental benefits include reduced pollution and soil degradation. Nutritional differences compared to conventional foods are minimal.",
    "gluten free diet": "Gluten-free diets are essential for those with celiac disease or non-celiac gluten sensitivity. For others, there's little evidence of health benefits. Focus on naturally gluten-free whole foods rather than processed alternatives.",

    # Fallback responses
    "default": "I don't have specific information on that health topic. For personalized medical advice, please consult with a healthcare professional.",
    "greeting": "Hello! I'm PASMA's health assistant. How can I help you with your health questions today?",
    "thanks": "You're welcome! Is there anything else I can help you with regarding your health?",
    "goodbye": "Take care and stay healthy! Feel free to return if you have more health questions.",
    "help": "I can provide general information about common health topics, symptoms, and wellness tips. What would you like to know about?",
    "disclaimer": MEDICAL_DISCLAIMER
}


# Function to find the best match for user input
def find_best_match(user_input):
    user_input = user_input.lower()

    # Check for exact matches first
    if user_input in responses:
        return responses[user_input]

    # Check for greetings
    if re.search(r'\b(hi|hello|hey|greetings)\b', user_input):
        return responses["greeting"]

    # Check for thanks
    if re.search(r'\b(thanks|thank you|appreciate it)\b', user_input):
        return responses["thanks"]

    # Check for goodbyes
    if re.search(r'\b(bye|goodbye|see you|farewell)\b', user_input):
        return responses["goodbye"]

    # Check for help requests
    if re.search(r'\b(help|assist|support)\b', user_input):
        return responses["help"]

    # Check for partial matches
    best_match = None
    highest_score = 0

    for key in responses:
        if key in ["default", "greeting", "thanks", "goodbye", "help", "disclaimer"]:
            continue

        # Calculate match score based on word overlap
        key_words = set(key.split())
        input_words = set(user_input.split())
        common_words = key_words.intersection(input_words)

        if common_words:
            score = len(common_words) / len(key_words)
            if score > highest_score:
                highest_score = score
                best_match = key

    # Return the best match if score is above threshold, otherwise default response
    if best_match and highest_score > 0.3:
        return responses[best_match]
    else:
        return responses["default"]

