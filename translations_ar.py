"""Arabic translations for the Takwa Foods site.

Keys are the exact English strings as they appear in the HTML text nodes, so
build_arabic.py can look each one up while walking a page. Anything missing
from this table is left in English rather than guessed at, and build_arabic.py
reports it, so an untranslated string shows up as a warning instead of
silently shipping.

Brand and proper names keep their usual Arabic spellings: Takwa Foods is
تقوى للأغذية, Flavora is فلافورا, Enna is إينا, Nestle is نستله.

The Arabic here is a first pass and should be read by a native speaker before
this goes public -- it is marketing copy for a real company.
"""
import json
import os

AR = {
    # ---------------- navigation / header ----------------
    "Home": "الرئيسية",
    "Home Page": "الصفحة الرئيسية",
    "About Us": "من نحن",
    "Our Products": "منتجاتنا",
    "Our Brands": "علاماتنا التجارية",
    "Flavora Cafe": "فلافورا كافيه",
    "Flavora": "فلافورا",
    "Blogs": "المدونة",
    "English": "English",
    "Arabic": "العربية",
    "Get In Touch": "تواصل معنا",
    "get in touch": "تواصل معنا",
    "contact us": "اتصل بنا",
    "Contact Us": "اتصل بنا",

    # ---------------- home: hero ----------------
    "From Our Roots": "من جذورنا",
    "to Your Shelves": "إلى رفوفكم",

    # ---------------- home: about ----------------
    "about us": "من نحن",
    "Leaders in Food Manufacturing and Packaging": "روّاد في تصنيع وتغليف الأغذية",
    "Get to Know": "تعرّف على",
    "Takwa Foods": "تقوى للأغذية",
    "At Takwa Foods, everything starts with our customer. We believe in building strong, transparent partnerships based on trust, responsiveness, and shared growth. Our team culture values agility, collaboration, and long-term thinking, making us easy to work with and committed to doing things right.":
        "في تقوى للأغذية، يبدأ كل شيء من عملائنا. نؤمن ببناء شراكات قوية وشفافة قائمة على الثقة وسرعة الاستجابة والنمو المشترك. تقوم ثقافة فريقنا على المرونة والتعاون والتفكير بعيد المدى، ما يجعل التعامل معنا سهلاً، والتزامنا بإتقان العمل ثابتاً.",
    "Trusted Partner Since 1996": "شريك موثوق منذ عام 1996",
    "Empowering Brands to Grow": "نمكّن العلامات التجارية من النمو",

    # ---------------- home: services ----------------
    "Service": "خدماتنا",
    "Explore Our Manufacturing": "اكتشف خبراتنا",
    "Expertise and Services": "وخدماتنا التصنيعية",
    "Recipes & Flavors Development": "تطوير الوصفات والنكهات",
    "Our team of R&D experts crafts innovative and delicious recipes, along with unique flavors tailored to your needs. Whether you're looking to create a new taste or enrich existing, we bring creativity and expertise to every recipe and flavor that we develop per customer demand.":
        "يبتكر فريق البحث والتطوير لدينا وصفات مبتكرة وشهية، إلى جانب نكهات فريدة مصمّمة خصيصاً لاحتياجاتكم. سواء كنتم تسعون إلى ابتكار طعم جديد أو إثراء طعم قائم، نضع الإبداع والخبرة في كل وصفة ونكهة نطوّرها بحسب طلب العميل.",
    "Co-manufacturing Services": "خدمات التصنيع المشترك",
    "We provide flexible co-manufacturing services for coffee mixes, powdered milk, soups, and sachet-based foods. From recipe development and sourcing to production and final packaging, we help partners bring high-quality products to market with confidence.":
        "نقدّم خدمات تصنيع مشترك مرنة لخلطات القهوة والحليب المجفف والشوربات والأغذية المعبأة في أكياس. من تطوير الوصفة وتأمين المواد الأولية وصولاً إلى الإنتاج والتغليف النهائي، نساعد شركاءنا على طرح منتجات عالية الجودة في السوق بثقة.",
    "Private Label Food Manufacturing": "تصنيع الأغذية بعلامتكم التجارية",
    "We offer end-to-end private label services, helping you launch your own branded products with confidence. From flavor development to packaging design, our team ensures your products reflect your vision, backed by our manufacturing precision and quality standards.":
        "نوفّر خدمات متكاملة للتصنيع بعلامتكم التجارية، لمساعدتكم على إطلاق منتجاتكم الخاصة بثقة. من تطوير النكهة إلى تصميم العبوة، يحرص فريقنا على أن تعكس منتجاتكم رؤيتكم، مدعومة بدقّة التصنيع ومعايير الجودة لدينا.",
    "Custom Seasoning & Spice Blends": "خلطات البهارات والتوابل المخصّصة",
    "Our team develops tailor-made spice mixes and seasonings for food brands and manufacturers. Whether enhancing an existing recipe or creating something new, we work closely with clients to deliver consistent flavor, texture, and performance in every batch, every time.":
        "يطوّر فريقنا خلطات بهارات وتوابل مصمّمة خصيصاً للعلامات التجارية ومصنّعي الأغذية. سواء لتحسين وصفة قائمة أو ابتكار وصفة جديدة، نعمل عن قرب مع عملائنا لضمان ثبات النكهة والقوام والأداء، في كل دفعة، وفي كل مرة.",

    # ---------------- home: partners / video / stats ----------------
    "TESTIMONIALS": "شركاؤنا",
    "Our": "شركاؤنا",
    "Partners": "حول العالم",
    "At Takwa Foods, we provide top-quality food manufacturing, custom blends, and co-packing services tailored to meet global standards and diverse customer needs.":
        "في تقوى للأغذية، نقدّم تصنيعاً غذائياً عالي الجودة، وخلطات مخصّصة، وخدمات تعبئة مشتركة مصمّمة لتلبية المعايير العالمية واحتياجات عملائنا المتنوعة.",
    "TAKWA VIDEO": "فيديو تقوى",
    "Inside Takwa Foods, Factory Tour & Vision": "داخل تقوى للأغذية: جولة في المصنع ورؤيتنا",
    "watch video": "شاهد الفيديو",
    "Years In Business": "عاماً من العمل",
    "Employees": "موظف",
    "Products": "منتج",
    "Clients": "عميل",

    # ---------------- home: news ----------------
    "Recent News": "آخر الأخبار",
    "Latest News and Events by": "آخر الأخبار والفعاليات من",
    "Welcome to": "مرحباً بكم في",
    "Takwa News": "أخبار تقوى",
    "Quality Begins with Every Test": "الجودة تبدأ من كل اختبار",
    "At Takwa Foods, every product undergoes rigorous quality and safety testing to e...":
        "في تقوى للأغذية، يخضع كل منتج لاختبارات جودة وسلامة صارمة قبل...",
    "At Takwa Foods, every product undergoes rigorous quality and safety testing to ensure it meets the highest international standards before reaching our customers.":
        "في تقوى للأغذية، يخضع كل منتج لاختبارات جودة وسلامة صارمة لضمان مطابقته لأعلى المعايير الدولية قبل وصوله إلى عملائنا.",
    "Delivering Freshness Across the Region": "نوصل الطزاجة إلى كل أنحاء المنطقة",
    "Our modern distribution fleet ensures that every product is transported efficien...":
        "يضمن أسطول التوزيع الحديث لدينا نقل كل منتج بكفاءة...",
    "Our modern distribution fleet ensures that every product is transported efficiently, maintaining freshness and quality from our facilities to your shelves.":
        "يضمن أسطول التوزيع الحديث لدينا نقل كل منتج بكفاءة، مع الحفاظ على الطزاجة والجودة من منشآتنا إلى رفوفكم.",
    "Flavora Cafe Opens Its Doors": "فلافورا كافيه يفتح أبوابه",
    "Takwa is proud to announce the opening of Flavora Cafe, a space where our coffe...":
        "تفخر تقوى بالإعلان عن افتتاح فلافورا كافيه، مساحة تُقدَّم فيها قهوتنا...",
    "Introducing Enna Soups: Authentic Taste, Ready for Ramadan":
        "إينا.. طعم الأصالة يزيّن مائدتك في رمضان",
    "Just in time for the holy month of Ramadan, Takwa is proud to reveal our newest...":
        "مع حلول شهر رمضان المبارك، تفخر تقوى بالكشف عن أحدث...",
    "Learn More": "اقرأ المزيد",
    "More Info": "تفاصيل أكثر",

    # ---------------- footer ----------------
    "Get in Touch with Us": "تواصل معنا",
    "Get in Touch with": "تواصل مع",
    "Get in Touch with US": "تواصل معنا",
    "For any queries, please feel free to reach us and we will try to reply to you during the 24 hours.":
        "لأي استفسار، لا تتردّدوا في التواصل معنا وسنسعى للرد خلال 24 ساعة.",
    "Careers": "الوظائف",
    "Working Hours": "ساعات العمل",
    "from Sunday to Thursday 08:00 AM - 4:00 PM": "من الأحد إلى الخميس، 08:00 صباحاً - 4:00 مساءً",
    "Message": "الرسالة",
    "Send Message": "إرسال الرسالة",
    "send a message": "أرسل رسالة",
    "At Takwa Foods, we blend tradition and innovation to create high-quality food products that people love, with flavors that inspire and standards you can trust.":
        "في تقوى للأغذية، نمزج الأصالة بالابتكار لصناعة منتجات غذائية عالية الجودة يحبّها الناس، بنكهات تُلهم ومعايير تستحق ثقتكم.",
    "Popular links": "روابط مهمة",
    "Vacancies": "الوظائف الشاغرة",
    "Our Team": "فريقنا",
    "Explore Takwa": "استكشف تقوى",
    "Our Blogs": "مدوّنتنا",
    "OFFICE ADDRESS": "عنوان المكتب",
    "Al Kiswa Damascus country side, Syria": "الكسوة، ريف دمشق، سوريا",
    "Al Kiswa, Damascus Countryside, Syria": "الكسوة، ريف دمشق، سوريا",
    "EMAIL ADDRESS": "البريد الإلكتروني",
    "PHONE NUMBER": "رقم الهاتف",
    "Cookies": "ملفات تعريف الارتباط",
    "We use cookies to improve your browsing experience. By continuing, you agree to our use of cookies.":
        "نستخدم ملفات تعريف الارتباط لتحسين تجربة تصفّحكم. بمتابعتكم التصفّح، فإنكم توافقون على استخدامنا لها.",
    "Accept": "موافق",

    # ---------------- page banners ----------------
    "Delivering Excellence": "نقدّم التميّز",
    "Since 1996": "منذ عام 1996",
    "About": "من نحن",
    "Blog Details": "تفاصيل المقال",

    "Welcome to Takwa": "أهلاً بكم في تقوى",
    "Three lines. 10,000+ tons a year.": "ثلاثة خطوط إنتاج. أكثر من 10,000 طن سنوياً.",
    # ---------------- careers ----------------
    "Careers at": "وظائف في",
    # ---------------- apply form ----------------
    "About you": "عنك",
    "The role": "الوظيفة",
    "Experience": "الخبرة",
    "Finish": "الإنهاء",
    "Back": "رجوع",
    "Continue": "متابعة",
    "Add another institution": "إضافة مؤسسة أخرى",
    "Add another certification": "إضافة شهادة أخرى",
    "Add another role": "إضافة وظيفة أخرى",
    "Add another referee": "إضافة معرّف آخر",
    "Most recent first. Add more rows only if you need them.": "الأحدث أولاً. أضف صفوفاً إضافية عند الحاجة فقط.",
    "Most recent first. Leave any you do not need blank.": "الأحدث أولاً. اترك ما لا تحتاجه فارغاً.",
    "Current or most recent role first.": "الوظيفة الحالية أو الأحدث أولاً.",
    "Five short steps. Your answers are kept as you type, so you can come back to it. A CV may be sent alongside this form but does not replace it.":
        "خمس خطوات قصيرة. تُحفظ إجاباتك أثناء الكتابة، فيمكنك العودة إليها لاحقاً. يمكن إرسال السيرة الذاتية مع هذا النموذج لكنها لا تغني عنه.",
    "Where you answer “Yes”, give brief details below. A request for an adjustment is treated confidentially and has no bearing on the selection decision.":
        "عند الإجابة بـ«نعم»، يُرجى ذكر تفاصيل مختصرة أدناه. تُعامل طلبات التسهيلات بسرّية ولا تؤثر على قرار الاختيار.",
    "Open the application form": "افتح نموذج التقديم",
    "Fill it in here, or": "املأه هنا، أو",
    "download it as Word": "حمّله بصيغة Word",
    "Employment": "طلب",
    "application": "توظيف",
    "Apply to": "التقديم إلى",
    "Complete every section in English, in full. Incomplete forms may not be processed. A CV may be sent alongside this form but does not replace it. All statements are subject to verification.":
        "يُرجى إكمال كل قسم بالإنجليزية وبشكل كامل. قد لا تُعالج الطلبات غير المكتملة. يمكن إرسال السيرة الذاتية مع هذا النموذج لكنها لا تغني عنه. جميع البيانات خاضعة للتحقق.",
    "Prefer to work offline?": "تفضّل العمل دون اتصال؟",
    "Download the same form as a Word document": "حمّل النموذج نفسه بصيغة Word",
    "and email it to": "وأرسله إلى",
    "Vacancy reference": "الرقم المرجعي للشاغر",
    "Date of application": "تاريخ التقديم",
    "Personal details": "البيانات الشخصية",
    "Full legal name": "الاسم القانوني الكامل",
    "Nationality": "الجنسية",
    "Date of birth": "تاريخ الميلاد",
    "Mobile number": "رقم الجوال",
    "Alternative number": "رقم بديل",
    "Email address": "البريد الإلكتروني",
    "LinkedIn / portfolio URL": "رابط لينكدإن أو أعمالك",
    "Hold a valid driving licence?": "هل تحمل رخصة قيادة سارية؟",
    "Select…": "اختر…",
    "Yes": "نعم",
    "No": "لا",
    "Current residential address": "عنوان السكن الحالي",
    "Position applied for": "الوظيفة المتقدَّم لها",
    "Employment type": "نوع التوظيف",
    "Full-time": "دوام كامل",
    "Part-time": "دوام جزئي",
    "Fixed-term contract": "عقد محدد المدة",
    "Consultant / Freelance": "استشاري / عمل حر",
    "Internship": "تدريب",
    "Work arrangement": "نمط العمل",
    "On-site": "في الموقع",
    "Hybrid": "مختلط",
    "Remote": "عن بُعد",
    "No preference": "لا تفضيل",
    "Available start date": "تاريخ المباشرة المتاح",
    "Notice period required": "مدة الإشعار المطلوبة",
    "Expected gross salary": "الراتب الإجمالي المتوقع",
    "How did you learn of this vacancy?": "كيف عرفت بهذا الشاغر؟",
    "Previously applied to or employed by us?": "هل تقدّمت أو عملت لدينا سابقاً؟",
    "If yes, dates and details": "إن كان نعم، التواريخ والتفاصيل",
    "Education": "التعليم",
    "Most recent first.": "الأحدث أولاً.",
    "Institution 1": "المؤسسة 1",
    "Institution": "المؤسسة",
    "Qualification & major": "المؤهل والتخصص",
    "From": "من",
    "To": "إلى",
    "Grade / result": "التقدير / النتيجة",
    "Institution 2": "المؤسسة 2",
    "Institution 3": "المؤسسة 3",
    "Certifications & licences": "الشهادات والتراخيص",
    "Certification 1": "شهادة 1",
    "Certification / licence": "الشهادة أو الترخيص",
    "Issuing body": "الجهة المانحة",
    "Issued": "تاريخ الإصدار",
    "Expires": "تاريخ الانتهاء",
    "Credential ID": "رقم الوثيقة",
    "Certification 2": "شهادة 2",
    "Certification 3": "شهادة 3",
    "Employment history": "الخبرات العملية",
    "Current or most recent first.": "الوظيفة الحالية أو الأحدث أولاً.",
    "Role 1": "وظيفة 1",
    "Employer name & industry": "اسم جهة العمل والقطاع",
    "Job title": "المسمى الوظيفي",
    "Reporting to (job title)": "المسؤول المباشر (المسمى الوظيفي)",
    "Key responsibilities & measurable achievements": "أبرز المسؤوليات والإنجازات القابلة للقياس",
    "Final salary & benefits": "آخر راتب والمزايا",
    "Reason for leaving": "سبب ترك العمل",
    "Role 2": "وظيفة 2",
    "Role 3": "وظيفة 3",
    "Skills, systems & languages": "المهارات والأنظمة واللغات",
    "Core functional / technical skills": "المهارات الأساسية والتقنية",
    "Software, systems & tools": "البرمجيات والأنظمة والأدوات",
    "State your proficiency level for each.": "اذكر مستوى إتقانك لكل منها.",
    "Languages": "اللغات",
    "State your level in each: spoken and written.": "اذكر مستواك في كل لغة: تحدثاً وكتابة.",
    "Additional information": "معلومات إضافية",
    "Why are you applying, and what makes you a strong fit?": "لماذا تتقدّم لهذه الوظيفة، وما الذي يجعلك مناسباً لها؟",
    "Maximum 250 words.": "بحد أقصى 250 كلمة.",
    "Explanation of any employment gap of three months or more": "توضيح أي انقطاع عن العمل لثلاثة أشهر أو أكثر",
    "Where you answer “Yes”, give brief details. A request for an adjustment is treated confidentially and has no bearing on the selection decision.":
        "عند الإجابة بـ«نعم»، يُرجى ذكر تفاصيل مختصرة. تُعامل طلبات التسهيلات بسرّية ولا تؤثر على قرار الاختيار.",
    "Related to, or in a relationship with, any employee, director or shareholder?":
        "هل تربطك صلة قرابة أو علاقة بأي موظف أو مدير أو مساهم لدينا؟",
    "Hold any other directorship, business interest or secondary employment?":
        "هل لديك أي عضوية إدارة أو مصلحة تجارية أو عمل آخر؟",
    "Currently employed?": "هل تعمل حالياً؟",
    "Willing to work shifts?": "هل لديك استعداد للعمل بنظام الورديات؟",
    "Any relatives currently working for this organisation?": "هل لديك أقارب يعملون حالياً لدى الشركة؟",
    "Details for any “Yes” answered above": "تفاصيل أي إجابة بـ«نعم» أعلاه",
    "References": "المعرّفون",
    "Two referees, at least one a direct line manager from a recent role. Referees are contacted only with your consent.":
        "معرّفان اثنان، أحدهما على الأقل مسؤول مباشر في وظيفة حديثة. لا يتم التواصل معهما إلا بموافقتك.",
    "Referee 1": "معرّف 1",
    "Full name": "الاسم الكامل",
    "Job title & organisation": "المسمى الوظيفي وجهة العمل",
    "Relationship to you": "صلته بك",
    "Email": "البريد الإلكتروني",
    "Telephone": "الهاتف",
    "Referee 2": "معرّف 2",
    "Data protection & consent": "حماية البيانات والموافقة",
    "The personal data you provide is collected and processed solely for the purpose of assessing your suitability for employment. It is retained for the period stated in our recruitment privacy notice and is not disclosed to any third party without your consent, save where required by law. You may at any time request access to, correction of, or erasure of your data by contacting the address given in that notice.":
        "تُجمع بياناتك الشخصية وتُعالَج لغرض تقييم مدى ملاءمتك للتوظيف فقط. وتُحفظ للمدة المذكورة في إشعار خصوصية التوظيف لدينا، ولا يتم الإفصاح عنها لأي طرف ثالث دون موافقتك، إلا حيث يقتضي القانون. ويمكنك في أي وقت طلب الاطلاع على بياناتك أو تصحيحها أو حذفها عبر العنوان المذكور في ذلك الإشعار.",
    "I consent to the processing of my personal data for the purposes described above.":
        "أوافق على معالجة بياناتي الشخصية للأغراض الموضحة أعلاه.",
    "I consent to my details being retained for consideration for other suitable vacancies.":
        "أوافق على الاحتفاظ ببياناتي للنظر فيها لشواغر أخرى مناسبة.",
    "10": "10",
    "Declaration": "الإقرار",
    "I declare that the information given in this form is true, complete and accurate to the best of my knowledge. I understand that any false statement, omission or misrepresentation may result in the withdrawal of an offer of employment or, if already appointed, in disciplinary action up to and including dismissal. I authorise the organisation to verify the information provided, including qualifications, employment history and references, subject to the consents given above and to applicable law.":
        "أقرّ بأن المعلومات الواردة في هذا النموذج صحيحة وكاملة ودقيقة على حد علمي. وأدرك أن أي بيان غير صحيح أو إغفال أو تضليل قد يؤدي إلى سحب عرض العمل، أو إلى إجراءات تأديبية تصل إلى إنهاء الخدمة إن كنت قد عُيّنت. وأفوّض الشركة بالتحقق من المعلومات المقدَّمة، بما فيها المؤهلات والخبرات والمعرّفين، وفقاً للموافقات الممنوحة أعلاه وللقانون المعمول به.",
    "I agree to the declaration above.": "أوافق على الإقرار أعلاه.",
    "Applicant full name": "الاسم الكامل لمقدّم الطلب",
    "Date": "التاريخ",
    "Submit application": "إرسال الطلب",
    "Fields marked": "الحقول المعلَّمة بـ",
    "are required. Send your CV separately to": "مطلوبة. أرسل سيرتك الذاتية بشكل منفصل إلى",
    "quoting the position.": "مع ذكر اسم الوظيفة.",
    "Apply with our form": "قدّم عبر نموذجنا",
    "Ten short sections covering your details, education, employment history and references. Fill it in, save it, and email it back to us.":
        "عشرة أقسام قصيرة تشمل بياناتك وتعليمك وخبراتك العملية ومعرّفيك. املأه واحفظه وأعده إلينا بالبريد الإلكتروني.",
    "Download the application form": "حمّل نموذج التقديم",
    "Word document, 80 KB": "ملف Word، 80 كيلوبايت",
    "Or just send a CV": "أو أرسل سيرتك الذاتية فقط",
    "If you would rather not fill in a form, a CV and a short note about the work you want to do is enough to start a conversation.":
        "إن كنت تفضّل عدم ملء نموذج، تكفي سيرة ذاتية وسطور قصيرة عن العمل الذي ترغب به لبدء الحديث.",
    "Email us your CV": "أرسل سيرتك بالبريد",
    "Make food the region": "اصنع غذاءً تثق به",
    "already trusts.": "المنطقة بالفعل.",
    "Where you": "أين",
    "would work": "ستعمل",
    "The teams": "الفرق التي",
    "we hire into": "نوظّف فيها",
    "How hiring": "كيف يجري",
    "works here": "التوظيف لدينا",
    "positions": "الشاغرة",
    "Nothing listed": "لا تجد ما",
    "that fits?": "يناسبك؟",
    "We have manufactured in Syria since 1996, from a single plant in Al Kiswa. Our lines fill supermarket shelves under our own brands, Flavora and Enna, and under the labels of companies who ask us to make their products for them. It is careful, exacting work, and the people who do it stay.":
        "نصنّع في سوريا منذ عام 1996، من مصنع واحد في الكسوة. تملأ خطوطنا رفوف الأسواق تحت علامتينا الخاصتين، فلافورا وإينا، وتحت علامات شركات تطلب منّا تصنيع منتجاتها. إنه عمل دقيق ومتقن، ومن يقوم به يبقى معنا.",
    "One site, in Al Kiswa, Damascus Countryside. Three production lines, coffee, dairy and culinary, each with its own air handling unit, inline metal detection and a two-stage sieve and magnet, so the three never share air or equipment.":
        "موقع واحد في الكسوة بريف دمشق. ثلاثة خطوط إنتاج: القهوة والألبان والأغذية، لكل خط وحدة تكييف هواء خاصة به، وكشف معادن على الخط، ومنخل ومغناطيس بمرحلتين، فلا تتشارك الخطوط الثلاثة الهواء ولا المعدّات.",
    "Most of our hiring happens in these six areas. If your experience sits in one of them, we would like to hear from you whether or not a matching role is listed below.":
        "يتركّز توظيفنا في هذه المجالات الستة. إن كانت خبرتك في أحدها، يسعدنا أن نسمع منك سواء وُجد شاغر مطابق أدناه أم لا.",
    "Four steps, and we tell you where you stand at each one. You will hear back either way.":
        "أربع خطوات، ونطلعك على موقفك في كل منها. سنعود إليك بالرد في الحالتين.",
    "Roles we are actively recruiting for right now.": "الوظائف التي نوظّف لها فعلياً الآن.",
    "We hire steadily rather than in bulk, so the right person often reaches us before the role is written. Send us your CV with the area you work in, and we will keep it on file and come back to you when something opens.":
        "نوظّف باستمرار لا بأعداد كبيرة دفعة واحدة، ولذلك يصلنا الشخص المناسب غالباً قبل أن تُكتب الوظيفة. أرسل سيرتك الذاتية مع مجال عملك، وسنحتفظ بها ونعود إليك عند توفّر شاغر.",
    "Send us your CV": "أرسل سيرتك الذاتية",
    "Three decades of continuous manufacturing": "ثلاثة عقود من التصنيع المتواصل",
    "225 people": "225 موظفاً",
    "Production, quality, R&D, supply chain and commercial": "الإنتاج والجودة والبحث والتطوير وسلسلة التوريد والمبيعات",
    "Approved by Nestlé": "مورّد معتمد لدى نستله",
    "A supplier since 2004, and their factory partner 2007 to 2013":
        "مورّد منذ 2004، وشريك التصنيع لديها من 2007 إلى 2013",
    "Two own brands": "علامتان خاصتان",
    "Flavora coffee and Enna soups, made start to finish here": "قهوة فلافورا وشوربات إينا، تُصنع هنا من البداية إلى النهاية",
    "Food safety": "سلامة الغذاء",
    "Managed to ISO 22000 principles, alongside HACCP and Halal requirements":
        "تُدار وفق مبادئ ISO 22000، إلى جانب متطلبات HACCP والحلال",
    "Working week": "أيام العمل",
    "Sunday to Thursday, 08:00 to 16:00, on site": "من الأحد إلى الخميس، 08:00 حتى 16:00، في الموقع",
    "Production & Operations": "الإنتاج والعمليات",
    "Line operators, shift leads, packaging, maintenance and engineering.":
        "مشغّلو الخطوط ورؤساء الورديات والتغليف والصيانة والهندسة.",
    "QA and QC, laboratory analysis, hygiene, audits and certification.":
        "ضمان ومراقبة الجودة، والتحاليل المخبرية، والنظافة، والتدقيق والشهادات.",
    "Research & Development": "البحث والتطوير",
    "Recipe and flavour development, seasoning blends, trials and scale-up.":
        "تطوير الوصفات والنكهات، وخلطات التوابل، والتجارب والتوسّع في الإنتاج.",
    "Supply Chain & Warehousing": "سلسلة التوريد والمستودعات",
    "Procurement, raw materials, planning, stock control and dispatch.":
        "المشتريات والمواد الأولية والتخطيط وضبط المخزون والشحن.",
    "Sales & Commercial": "المبيعات والتجارة",
    "Private label accounts, co-manufacturing, export and brand sales.":
        "حسابات العلامات الخاصة، والتصنيع المشترك، والتصدير، ومبيعات العلامات.",
    "Finance & Administration": "المالية والإدارة",
    "Accounting, payroll, human resources and office management.": "المحاسبة والرواتب والموارد البشرية وإدارة المكتب.",
    "You apply": "تتقدّم بطلبك",
    "Send your CV and a short note about the work you want to do.": "أرسل سيرتك الذاتية وسطوراً قصيرة عن العمل الذي ترغب به.",
    "First conversation": "المكالمة الأولى",
    "A call with the hiring manager about your experience and the role.":
        "مكالمة مع مسؤول التوظيف حول خبرتك والوظيفة.",
    "Visit the plant": "زيارة المصنع",
    "Meet the team you would join and see the lines you would work on.":
        "تلتقي بالفريق الذي ستنضم إليه وترى الخطوط التي ستعمل عليها.",
    "Offer": "العرض",
    "Terms in writing, with a start date agreed to suit your notice period.":
        "شروط مكتوبة، مع تاريخ مباشرة يُتفق عليه بما يناسب فترة إشعارك.",
    "1 open position": "شاغر واحد",
    "Project management": "إدارة المشاريع",
    "Al Kiswa, Damascus": "الكسوة، دمشق",
    "Flavora Café": "فلافورا كافيه",
    "ISO 22000": "ISO 22000",

    # ---------------- about us ----------------
    "Driven By": "يقودنا",
    "Purpose and Passion": "الهدف والشغف",
    # the figure is now a run-time counter, so the sentence is split either
    # side of it rather than carrying the number in the string
    "With": "مع",
    "Since 1996": "منذ عام 1996",
    "Years in Business": "عاماً من العمل",
    "years in business, at Takwa Foods, everything starts with our customer. We believe in building strong, transparent partnerships based on trust, responsiveness, and shared growth. Our team culture values agility, collaboration, and long-term thinking, making us easy to work with and committed to doing things right.":
        "عاماً من العمل، يبدأ كل شيء في تقوى للأغذية من عملائنا. نؤمن ببناء شراكات قوية وشفافة قائمة على الثقة وسرعة الاستجابة والنمو المشترك. تقوم ثقافة فريقنا على المرونة والتعاون والتفكير بعيد المدى، ما يجعل التعامل معنا سهلاً، والتزامنا بإتقان العمل ثابتاً.",
    "years in business": "عاماً من العمل",
    "With over": "مع أكثر من",
    "32 years in business": "32 عاماً من العمل",
    ", at Takwa Foods, everything starts with our customer. We believe in building strong, transparent partnerships based on trust, responsiveness, and shared growth. Our team culture values agility, collaboration, and long-term thinking, making us easy to work with and committed to doing things right.":
        "، يبدأ كل شيء في تقوى للأغذية من عملائنا. نؤمن ببناء شراكات قوية وشفافة قائمة على الثقة وسرعة الاستجابة والنمو المشترك. تقوم ثقافة فريقنا على المرونة والتعاون والتفكير بعيد المدى، ما يجعل التعامل معنا سهلاً، والتزامنا بإتقان العمل ثابتاً.",
    "With over 32 years in business, at Takwa Foods, everything starts with our customer. We believe in building strong, transparent partnerships based on trust, responsiveness, and shared growth. Our team culture values agility, collaboration, and long-term thinking, making us easy to work with and committed to doing things right.":
        "مع أكثر من 32 عاماً من العمل، يبدأ كل شيء في تقوى للأغذية من عملائنا. نؤمن ببناء شراكات قوية وشفافة قائمة على الثقة وسرعة الاستجابة والنمو المشترك. تقوم ثقافة فريقنا على المرونة والتعاون والتفكير بعيد المدى، ما يجعل التعامل معنا سهلاً، والتزامنا بإتقان العمل ثابتاً.",
    "Since 1996, we've evolved from a local supplier into a leading force in the regional food industry. We've developed deep expertise in flavors, seasonings, and premium, and we support our partners with tailored co-manufacturing and private label solutions. Our products are built on quality, precision, and consistency, but it’s our relationships that truly set us apart.":
        "منذ عام 1996، تطوّرنا من مورّد محلي إلى قوة رائدة في صناعة الأغذية على مستوى المنطقة. راكمنا خبرة عميقة في النكهات والتوابل والمنتجات المميّزة، وندعم شركاءنا بحلول تصنيع مشترك وعلامات خاصة مصمّمة لهم. منتجاتنا مبنيّة على الجودة والدقّة والثبات، لكن علاقاتنا هي ما يميّزنا حقاً.",
    "Since 1996, we've evolved from a local supplier into a leading force in the regi...":
        "منذ عام 1996، تطوّرنا من مورّد محلي إلى قوة رائدة في صناعة...",
    "Since 1996, we've evolved from a local supplier into a leading force in the regional food industry. We've developed deep expertise in flavors, seasonings, and premium, and we support our partners with tailored co-manufacturing and private label solutions.":
        "منذ عام 1996، تطوّرنا من مورّد محلي إلى قوة رائدة في صناعة الأغذية على مستوى المنطقة. راكمنا خبرة عميقة في النكهات والتوابل والمنتجات المميّزة، وندعم شركاءنا بحلول تصنيع مشترك وعلامات خاصة مصمّمة لهم.",

    "Vision": "الرؤية",
    "Our Vision, What Guides Every Step We Take": "رؤيتنا، ما يوجّه كل خطوة نخطوها",
    "Bridging global cultures through the universal language of food.":
        "نصل بين ثقافات العالم عبر لغة الطعام التي يفهمها الجميع.",
    "Mission": "الرسالة",
    "Our Mission, What Fuels Everything We Do": "رسالتنا، ما يدفع كل ما نقوم به",
    "To lead locally in food production by improving processes, ensuring authentic products are accessible and affordable, and sustainably increasing production to meet market needs.":
        "أن نكون روّاداً محلياً في إنتاج الأغذية عبر تطوير عملياتنا، وضمان أن تبقى المنتجات الأصيلة متاحة وبأسعار في متناول الجميع، وزيادة الإنتاج بشكل مستدام لتلبية حاجة السوق.",

    "Our History": "تاريخنا",
    "Milestones That": "محطات",
    "Shaped Our Legacy": "صنعت إرثنا",
    "Takwa’s journey began in 1996 with a simple idea: drying parsley to preserve freshness and quality. That early vision evolved into a full-scale operation focused on sourcing and supplying the finest raw ingredients to some of the most respected food companies locally and internationally.":
        "بدأت رحلة تقوى عام 1996 بفكرة بسيطة: تجفيف البقدونس للحفاظ على طزاجته وجودته. تحوّلت تلك الرؤية المبكرة إلى عمل متكامل يركّز على تأمين وتوريد أجود المواد الأولية لبعض أعرق شركات الأغذية محلياً ودولياً.",
    "From 2007 till now, we became an approved supplier for Nestlé, providing high-quality raw materials. This partnership soon expanded into manufacturing, as we began producing Nescafé in Syria, later adding SKUs like Nido and other Nestlé coffee products.":
        "منذ عام 2007 وحتى اليوم، أصبحنا مورّداً معتمداً لدى نستله، نزوّدها بمواد أولية عالية الجودة. وسرعان ما اتسعت هذه الشراكة لتشمل التصنيع، فبدأنا بإنتاج نسكافيه في سوريا، ثم أضفنا منتجات أخرى مثل نيدو وسواها من منتجات نستله للقهوة.",
    "Building on this experience, we expanded into B2B manufacturing of spice mixes and seasonings for major food brands.":
        "وبناءً على هذه الخبرة، توسّعنا في تصنيع خلطات البهارات والتوابل لكبرى العلامات الغذائية ضمن قطاع الأعمال.",
    "We launched Presto, for Katakit, a pioneering food manufacturer in Syria which has since become one of the most recognized names in powdered soups and stocks in Syria.":
        "أطلقنا منتج بريستو لصالح كتاكيت، إحدى الشركات الرائدة في تصنيع الأغذية في سوريا، ليصبح منذ ذلك الحين من أبرز الأسماء في مجال الشوربات ومرقّات الطعام البودرة في سوريا.",
    "Today, we continue this legacy with the development of our own branded coffee line (Flavora) and premium soup range under our new brand Enna.":
        "واليوم، نواصل هذا الإرث بتطوير خط القهوة الخاص بنا (فلافورا) ومجموعة الشوربات المميّزة تحت علامتنا الجديدة إينا.",

    "Letter From Founder": "رسالة من المؤسّس",
    "A Message From": "رسالة من",
    "Our CEO": "مديرنا التنفيذي",
    "\"Don’t chase sales. Build loyalty customers love.\"":
        "«لا تلاحق المبيعات. ابنِ ولاءً يحبّه العملاء.»",
    "Great companies begin with great people. Empower them to create systems that deliver products so vital, they enrich everyday life. Loyalty grows from care and commitment.":
        "الشركات العظيمة تبدأ بأشخاص عظماء. امنحهم القدرة على بناء أنظمة تنتج منتجات أساسية تُثري الحياة اليومية. فالولاء ينمو من الاهتمام والالتزام.",
    "Khaled Takwa": "خالد تقوى",

    # ---------------- products / filters ----------------
    "Select Brand": "اختر العلامة التجارية",
    "Select Category": "اختر الفئة",
    "Enna": "إينا",
    "Creamer": "مبيّض القهوة",
    "Espresso Capsules": "كبسولات إسبريسو",
    "Instant Coffee": "قهوة سريعة التحضير",
    "Soups": "شوربات",
    "Clear filters": "مسح الفلاتر",
    "Search Now": "ابحث الآن",
    "Switch tab for list or grid view layout": "تبديل العرض بين القائمة والشبكة",
    "No products match these filters.": "لا توجد منتجات مطابقة لهذه الفلاتر.",

    "Mushroom Soup": "شوربة الفطر",
    "Creamy and rich, made with real mushrooms grown in Syria and dried in our own facility.":
        "كريمية وغنية، محضّرة من فطر حقيقي مزروع في سوريا ومجفّف في منشأتنا.",
    "Chicken Noodle Soup": "شوربة الدجاج بالشعيرية",
    "Real chicken, pre-dried in-house and ground into every serving, with enriched noodles.":
        "دجاج حقيقي، مجفّف لدينا ومطحون في كل حصة، مع شعيرية مدعّمة.",
    "Broccoli Soup": "شوربة البروكلي",
    "Smooth and creamy with real broccoli, dried in-house to lock in flavour and goodness.":
        "ناعمة وكريمية ببروكلي حقيقي، مجفّف لدينا للحفاظ على النكهة والقيمة الغذائية.",
    "Vegetable Soup": "شوربة الخضار",
    "More than ten real vegetables, all locally grown and dried in-house.":
        "أكثر من عشرة أنواع من الخضار الحقيقية، مزروعة محلياً ومجفّفة لدينا.",
    "Three-in-One": "ثلاثة في واحد",
    "Premium coffee with less sugar and rich coconut cream, for a smooth, balanced cup.":
        "قهوة فاخرة بسكر أقل وكريمة جوز هند غنية، لفنجان ناعم ومتوازن.",
    "Two-in-One": "اثنان في واحد",
    "Premium coffee with rich coconut creamer and a bold, strong profile.":
        "قهوة فاخرة مع مبيّض جوز الهند الغني ونكهة قوية وجريئة.",
    "Pure Coffee": "قهوة نقية",
    "Exceptionally pure, premium coffee that tastes incredible on its own or with any creamer.":
        "قهوة فاخرة بنقاء استثنائي، مذاقها رائع وحدها أو مع أي مبيّض.",
    "Coffee Creamer": "مبيّض القهوة",
    "A high-quality, non-dairy creamer made with coconut oil for a smooth, rich finish.":
        "مبيّض عالي الجودة خالٍ من الحليب، محضّر بزيت جوز الهند لقوام ناعم وغني.",
    "One hundred percent Arabica, sealed in nitrogen for maximum freshness.":
        "أرابيكا 100%، معبّأة في بيئة نيتروجين لأقصى درجات الطزاجة.",



    # --- homepage credibility sections added from the 8 Aug audit ---------
    "Trusted Since 1996": "شريك موثوق منذ 1996",
    "The name behind names": "الاسم خلف الأسماء",
    "you already know.": "التي تعرفونها بالفعل.",
    "For nearly three decades we have manufactured for the region's most demanding food brands. We became an approved Nestlé supplier in 2004 and served as their exclusive milk and coffee factory partner from 2007 to 2013, alongside private-label work for Katakit, Presto and others. That experience is now behind two brands of our own.":
        "على مدى ثلاثة عقود تقريباً، صنّعنا لأكثر العلامات الغذائية تطلّباً في المنطقة. أصبحنا مورّداً معتمداً لدى نستله عام 2004، وكنّا شريكهم الحصري لمصنع الحليب والقهوة من 2007 إلى 2013، إلى جانب أعمال التصنيع بالعلامة الخاصة لكتاكيت وبريستو وغيرهما. تلك الخبرة تقف اليوم خلف علامتين خاصتين بنا.",

    "Quality & Food Safety": "الجودة وسلامة الغذاء",
    "Built to global": "مبنيّ على معايير",
    "food-safety standards.": "سلامة الغذاء العالمية.",
    "Our food safety management system is implemented across all three production lines to ISO 22000 principles, alongside HACCP and Halal requirements. An internal readiness assessment is complete and formal certification is in progress.":
        "نظام إدارة سلامة الغذاء لدينا مطبّق على خطوط الإنتاج الثلاثة وفق مبادئ ISO 22000، إلى جانب متطلبات HACCP والحلال. اكتمل تقييم الجاهزية الداخلي، والشهادة الرسمية قيد الإنجاز.",
    "Every line runs its own dedicated air handling unit, inline metal detection, and a two-stage sieve and magnet, so coffee, dairy and culinary never share air or equipment.":
        "لكل خط وحدة تكييف هواء خاصة به، وكشف معادن ضمن الخط، ومنخل ومغناطيس على مرحلتين، بحيث لا تتشارك القهوة والألبان والأغذية الهواء أو المعدات إطلاقاً.",
    "ISO 22000, implemented": "ISO 22000، مطبّق",
    "HACCP": "HACCP",
    "Halal": "حلال",
    "ISO 9001 principles": "مبادئ ISO 9001",

    "Manufacturing Capability": "القدرة التصنيعية",
    "Three lines. 8,330 tons a year.": "ثلاثة خطوط. 8,330 طناً سنوياً.",
    "One standard.": "معيار واحد.",
    "Whether you need a single trial run or a national launch, the capacity is already in place, with warehousing headroom to grow into.":
        "سواء احتجتم إلى تشغيلة تجريبية واحدة أو إطلاق على مستوى البلاد، فالطاقة الإنتاجية جاهزة، مع مساحات تخزين تتيح مجالاً للنمو.",
    "Coffee mixes": "خلطات القهوة",
    "Dairy powders": "مساحيق الألبان",
    "Culinary & soups": "الأغذية والشوربات",
    "Warehousing": "التخزين",
    "— 4,230 t/yr · four filling machines, 5 g sachets to 1 kg packs":
        "— 4,230 طن/سنة · أربع آلات تعبئة، من أكياس 5 غ إلى عبوات 1 كغ",
    "— 3,000 t/yr · 350–900 g screw-fed packs with nitrogen flushing":
        "— 3,000 طن/سنة · عبوات 350–900 غ بتغذية لولبية وتعبئة بالنيتروجين",
    "— 1,100 t/yr · three-head filling": "— 1,100 طن/سنة · تعبئة بثلاثة رؤوس",
    "— 1,800 pallet positions, with capacity to spare":
        "— 1,800 موقع بالت، مع طاقة إضافية متاحة",

    "Sustainability": "الاستدامة",
    "Solar already runs": "الطاقة الشمسية تشغّل",
    "30–40% of our operations.": "30–40% من عملياتنا.",
    "Rooftop solar powers a substantial share of everything we make, and we are expanding it. Cleaner production, and a supply you can plan around regardless of grid conditions.":
        "تغذّي الألواح الشمسية على السطح جزءاً كبيراً من كل ما ننتجه، ونحن في طور التوسّع فيها. إنتاج أنظف، وإمداد يمكنكم التخطيط على أساسه مهما كانت أحوال الشبكة.",

    "Work With Us": "اعمل معنا",
    "Have a product idea?": "لديكم فكرة منتج؟",
    "We'll make it.": "نحن نصنعها.",
    "Recipe and flavour development, custom seasoning blends, co-manufacturing and private label, across coffee, dairy and culinary. Tell us what you are building and we will tell you exactly how we would produce it.":
        "تطوير الوصفات والنكهات، وخلطات البهارات المخصّصة، والتصنيع المشترك، والتصنيع بالعلامة الخاصة، في القهوة والألبان والأغذية. أخبرونا بما تبنونه وسنخبركم تماماً كيف سننتجه.",
    "Start a project": "ابدأ مشروعاً",

    '— 4,230 t/yr · four filling machines, 5\xa0g sachets to 1\xa0kg packs':
        '— 4,230 طن/سنة · أربع آلات تعبئة، من أكياس 5\xa0غ إلى عبوات 1\xa0كغ',
    '— 3,000 t/yr · 350–900\xa0g screw-fed packs with nitrogen flushing':
        '— 3,000 طن/سنة · عبوات 350–900\xa0غ بتغذية لولبية وتعبئة بالنيتروجين',
    # the products page banner
    "Get to know about": "تعرّف على",
    "our products": "منتجاتنا",

    # the three About Us bullets, written by the owner in the text editor
    "We make food properly, or we don't make it":
        "نصنع الغذاء كما يجب، أو لا نصنعه",
    "Real ingredients, from farms we know":
        "مكوّنات حقيقية، من مزارع نعرفها",
    "Now in our own brands: Flavora and Enna":
        "والآن في علامتينا الخاصتين: فلافورا وإينا",

    # ---------------- team ----------------
    "Khaldon Takwa": "خلدون تقوى",
    "Giath Takwa": "غياث تقوى",
    "Technology officer": "مسؤول التكنولوجيا",
    "co founder": "شريك مؤسّس",
    "CEO": "المدير التنفيذي",

    # names, transliterated -- worth a second pair of eyes, since a name has
    # no single correct spelling and these were read off photo filenames
    "Mohamad G Takwa": "محمد غياث تقوى",
    "Khaled Takwa": "خالد تقوى",
    "Soubhi Chammout": "صبحي شمعوط",
    "Mutassem Alsheikh": "معتصم الشيخ",
    "Khaldoun Takwa": "خلدون تقوى",
    "Majed Kousa": "ماجد كوسا",
    "Abdullah Maqsosah": "عبد الله مقصوصة",
    "Hussam Hammoud": "حسام حمود",
    "Mutaz Hamdan": "معتز حمدان",
    "Mohammad Al-Bazzal": "محمد البزال",
    "Ahmad Loda": "أحمد لودة",
    "Ammar Al Bitar": "عمار البيطار",
    "Bachir Al Taki": "بشير التقي",
    "Maher Alkhaled": "ماهر الخالد",
    "Alyaa Hamdan": "علياء حمدان",
    "Wadeh Youssef": "وضاح يوسف",
    "Bader Akkam": "بدر عكام",
    "Annie Khorozian": "آني خوروزيان",
    "Ahmad Safi": "أحمد صافي",
    "Ziad Echeh": "زياد عيشة",

    # job titles
    "Chairman and Founder": "رئيس مجلس الإدارة والمؤسّس",
    "Chief Operation Officer": "مدير العمليات",
    "Chief Business Officer": "مدير الأعمال",
    "Development and Innovation Officer": "مسؤول التطوير والابتكار",
    "Legal and Compliance Officer": "مسؤول الشؤون القانونية والامتثال",
    "Financial Manager": "المدير المالي",
    "National Sales Manager": "مدير المبيعات الوطني",
    "Research and Development Manager": "مدير البحث والتطوير",
    "Quality Manager": "مدير الجودة",
    "Production Manager": "مدير الإنتاج",
    "Supply Chain Manager": "مدير سلسلة التوريد",
    "Warehouse Manager": "مدير المستودعات",
    "Food and Beverage Manager": "مدير الأغذية والمشروبات",
    "HR Manager": "مدير الموارد البشرية",
    "Maintenance Manager": "مدير الصيانة",
    "Security and Services Manager": "مدير الأمن والخدمات",
    "Management Executive Assistant": "المساعِدة التنفيذية للإدارة",

    # ---------------- careers ----------------
    "About Takwa Food": "عن تقوى للأغذية",
    "Careers & Vacancies": "الوظائف والشواغر",
    "Open": "الوظائف",
    "Positions": "الشاغرة",
    "Don't’ miss the opportunity to work with us!": "لا تفوّت فرصة العمل معنا!",
    "Categories": "الفئات",
    "intern": "تدريب",
    "Senior Level": "مستوى خبرة",
    "2 open positions": "وظيفتان شاغرتان",
    "Project Manager & Consultant": "مدير مشاريع ومستشار",
    "Did not find your": "لم تجد",
    "position?": "وظيفتك؟",
    "We are always looking for new and young": "نبحث دائماً عن كفاءات شابة",
    "talents ready to expand our team": "جاهزة للانضمام إلى فريقنا",
    "Apply Now": "قدّم الآن",

    # ---------------- contact ----------------
    "Let's Talk": "لنتحدّث",
    "About Your Product": "عن منتجك",
    "How Can": "كيف يمكننا",
    "We Help You?": "مساعدتك؟",
    "Whether you're planning a new product, need a co-manufacturing partner, or want to talk about private label, our team is here to help.":
        "سواء كنت تخطّط لمنتج جديد، أو تبحث عن شريك تصنيع مشترك، أو ترغب بالحديث عن التصنيع بعلامتك الخاصة، فريقنا هنا لمساعدتك.",
    "Unlock your potential with expert guidance! Schedule a free consultation toward personal and business success.":
        "أطلق إمكاناتك بإرشاد الخبراء! احجز استشارة مجانية في طريقك نحو النجاح الشخصي والمهني.",
    "Contact Info": "معلومات التواصل",
    "WhatsApp": "واتساب",
    "Email Us": "راسلنا",
    "Visit Us": "زُرنا",

    # ---------------- product detail pages ----------------
    "Category:": "الفئة:",
    "Sizes Available": "العبوات المتوفرة",
    "Other Flavors": "نكهات أخرى",
    "Download Product Specs PDF": "حمّل مواصفات المنتج (PDF)",
    "About us": "من نحن",
    "About Us1": "من نحن",

    "Creamy and rich, made with real mushrooms grown in Syria and dried in our own facility. Wholesome, natural, and satisfying. Real ingredients, dried in-house.":
        "كريمية وغنية، محضّرة من فطر حقيقي مزروع في سوريا ومجفّف في منشأتنا. مغذية وطبيعية ومُشبعة. مكوّنات حقيقية، مجفّفة لدينا.",
    "Real chicken, pre-dried in-house and ground into every serving, paired with enriched noodles for a hearty, comforting bowl. Real ingredients, dried in-house.":
        "دجاج حقيقي، مجفّف لدينا ومطحون في كل حصة، مع شعيرية مدعّمة لطبق دافئ ومُشبع. مكوّنات حقيقية، مجفّفة لدينا.",
    "Smooth and creamy with real broccoli, dried in-house to lock in flavour and goodness. Real ingredients, dried in-house.":
        "ناعمة وكريمية ببروكلي حقيقي، مجفّف لدينا للحفاظ على النكهة والقيمة الغذائية. مكوّنات حقيقية، مجفّفة لدينا.",
    "More than ten real vegetables, all locally grown and dried in-house, for a nourishing, garden-fresh taste in every spoonful. Real ingredients, dried in-house.":
        "أكثر من عشرة أنواع من الخضار الحقيقية، مزروعة محلياً ومجفّفة لدينا، لمذاق مغذٍّ وطازج في كل ملعقة. مكوّنات حقيقية، مجفّفة لدينا.",
    "Premium coffee with less sugar and rich coconut cream, for a smooth, balanced cup. Premium coffee, crafted for our taste.":
        "قهوة فاخرة بسكر أقل وكريمة جوز هند غنية، لفنجان ناعم ومتوازن. قهوة فاخرة، مصنوعة على ذوقنا.",
    "Premium coffee with rich coconut creamer and a bold, strong profile that our region loves. Premium coffee, crafted for our taste.":
        "قهوة فاخرة مع مبيّض جوز الهند الغني ونكهة قوية وجريئة تحبّها منطقتنا. قهوة فاخرة، مصنوعة على ذوقنا.",
    "Exceptionally pure, premium coffee that tastes incredible on its own or with any creamer. Pure and strong. Premium coffee, crafted for our taste.":
        "قهوة فاخرة بنقاء استثنائي، مذاقها رائع وحدها أو مع أي مبيّض. نقية وقوية. قهوة فاخرة، مصنوعة على ذوقنا.",
    "A high-quality, non-dairy creamer made with coconut oil for a smooth, rich finish. Premium coffee, crafted for our taste.":
        "مبيّض عالي الجودة خالٍ من الحليب، محضّر بزيت جوز الهند لقوام ناعم وغني. قهوة فاخرة، مصنوعة على ذوقنا.",
    "One hundred percent Arabica, sealed in a nitrogen environment for maximum freshness. Available as a Brazilian blend at a higher roast, and a Colombian at a medium roast. Premium coffee, crafted for our taste.":
        "أرابيكا 100%، معبّأة في بيئة نيتروجين لأقصى درجات الطزاجة. متوفرة بخلطة برازيلية بتحميص أعلى، وأخرى كولومبية بتحميص متوسط. قهوة فاخرة، مصنوعة على ذوقنا.",
    "10 capsules": "10 كبسولات",

    "Since 1996, we've evolved from a local supplier into a leading force in the regional food industry. We've developed deep expertise in flavors, seasonings, and premium, and we support our partners with tailored co-manufacturing.":
        "منذ عام 1996، تطوّرنا من مورّد محلي إلى قوة رائدة في صناعة الأغذية على مستوى المنطقة. راكمنا خبرة عميقة في النكهات والتوابل والمنتجات المميّزة، وندعم شركاءنا بحلول تصنيع مشترك مصمّمة لهم.",

    "Sourced directly from natural crops grown on Syrian soil, we use advanced drying technology to lock in the rich flavor and nutritional value of every ingredient. Enna Soups are crafted to deliver that authentic, homemade taste without the long prep time. Real ingredients, dried in-house.":
        "من محاصيل طبيعية تُزرع في التربة السورية مباشرة، نستخدم تقنيات تجفيف متطوّرة للحفاظ على النكهة الغنية والقيمة الغذائية لكل مكوّن. صُنعت شوربات إينا لتمنحكم ذلك المذاق البيتي الأصيل دون وقت التحضير الطويل. مكوّنات حقيقية، مجفّفة لدينا.",

    # ---------------- blog articles ----------------
    "Takwa is proud to announce the opening of Flavora Cafe, a space where our coffee comes off the shelf and into the cup. Built around the Flavora brand, the cafe brings our instant coffee range into a setting designed for people to sit, relax, and taste it the way it was meant to be enjoyed.":
        "تفخر تقوى بالإعلان عن افتتاح فلافورا كافيه، مساحة تنتقل فيها قهوتنا من الرفّ إلى الفنجان. صُمّم المقهى حول علامة فلافورا، ليقدّم مجموعة قهوتنا سريعة التحضير في أجواء تدعو الناس للجلوس والاسترخاء وتذوّقها كما ينبغي أن تُذاق.",
    "Inside, the cafe serves the full Flavora range alongside the wider Takwa family of products, including our new Enna soups. It is somewhere the quality we build into every product can be experienced directly, from the first sip to the last.":
        "يقدّم المقهى مجموعة فلافورا كاملة إلى جانب عائلة منتجات تقوى الأوسع، بما فيها شوربات إينا الجديدة. إنه المكان الذي تُختبر فيه مباشرة الجودة التي نضعها في كل منتج، من الرشفة الأولى حتى الأخيرة.",
    "Whether you are stopping in for a quick coffee or settling in for a while, we would love to welcome you.":
        "سواء مررتم لتناول قهوة سريعة أو للجلوس بعض الوقت، يسعدنا أن نرحّب بكم.",
    "Just in time for the holy month of Ramadan, Takwa is proud to reveal our newest product line: Enna Soups.":
        "مع حلول شهر رمضان المبارك، تفخر تقوى بالكشف عن أحدث خطوط منتجاتها: شوربات إينا.",
    "Sourced directly from natural crops grown on Syrian soil, we use advanced drying technology to lock in the rich flavor and nutritional value of every ingredient.":
        "من محاصيل طبيعية تُزرع في التربة السورية مباشرة، نستخدم تقنيات تجفيف متطوّرة للحفاظ على النكهة الغنية والقيمة الغذائية لكل مكوّن.",
    "Enna Soups are crafted to deliver that authentic, homemade taste without the long prep time.":
        "صُنعت شوربات إينا لتمنحكم ذلك المذاق البيتي الأصيل دون وقت التحضير الطويل.",
    "Tag:": "الوسم:",
    "GO BACK": "العودة",

    # ---------------- careers detail ----------------
    "Company Overview:": "نبذة عن الشركة:",
    # the English page repeats this sentence twice; kept as-is so the two
    # versions stay in step
    "Since 1996, we've evolved from a local supplier into a leading force in the regional food industry. We've developed deep expertise in flavors, Since 1996, we've evolved from a local supplier into a leading force in the regional food industry. We've developed deep expertise in flavors,":
        "منذ عام 1996، تطوّرنا من مورّد محلي إلى قوة رائدة في صناعة الأغذية على مستوى المنطقة، وراكمنا خبرة عميقة في النكهات.",
    "Core Responsibilities:": "المهام الأساسية:",
    "Qualifications & Education Requirements": "المؤهلات والمتطلبات العلمية",
    "Manage daily operations and team coordination.": "إدارة العمليات اليومية وتنسيق عمل الفريق.",
    "Apply for this": "تقدّم لهذه",
    "position": "الوظيفة",
    "+ Upload Resume": "+ أرفق سيرتك الذاتية",
    "(max file size 15 mb)": "(الحد الأقصى لحجم الملف 15 ميغابايت)",
    "Location": "الموقع",
    "TYPE": "النوع",
    "DATE": "التاريخ",
    "DECLINE": "رفض",

    # ---------------- brand page ----------------
    "Download Brand PDF Catalog": "حمّل كتالوج العلامة (PDF)",
    "Visit Flavora Cafe": "زوروا موقع فلافورا كافيه",
    "Gallery": "معرض الصور",
    "Media": "المركز",
    "Center": "الإعلامي",

    # ---------------- B2B products page ----------------
    # Product names and their Arabic come from the company products sheet.
    # Anything without Arabic on that sheet is left out deliberately, so
    # build_arabic reports it as missing instead of it being guessed at.
    "for Business": "للأعمال",
    "For Business": "للأعمال",
    "Made for": "نصنّع لصالح",
    "other food businesses": "شركات أغذية أخرى",
    "Looking for something that is not on this list?":
        "تبحث عن شيء غير موجود في هذه القائمة؟",
    "Get in touch": "تواصل معنا",
    "B2B": "B2B",
    "B2C": "B2C",
    "These are the flavours, spices, sauces and seasonings we manufacture for food producers, restaurants and companies selling under their own label. Everything below is made at our plant in Al Kiswa. Talk to us about volumes, packaging and blends made to your own specification.":
        "هذه هي النكهات والبهارات والصوصات والتوابل التي نصنّعها لشركات الأغذية والمطاعم والشركات التي تبيع تحت علامتها الخاصة. كل ما يلي يُصنع في مصنعنا في الكسوة. تحدّث إلينا عن الكميات والتعبئة والخلطات المصنوعة حسب مواصفاتك.",
    "Flavors": "النكهات",
    "Chip and Snack Flavors": "نكهات الشيبس والموالح",
    "Smoked": "مدخن",
    "Barbecue": "باربكيو",
    "Salt & Vinegar": "ملح وخل",
    "Pizza": "بيتزا",
    "White Cheese": "جبنة بيضاء",
    "Red Cheese": "جبنة حمراء",
    "Ketchup": "كتشب",
    "Sweet & Spicy": "حار حلو",
    "Green Pepper": "فليفلة خضراء",
    "Spicy Lemon": "حار وليمون",
    "Extra Spicy": "حار نار",
    "Vegetable": "خضار",
    "Yellow Chicken": "دجاج اصفر",
    "White Chicken": "دجاج ابيض",
    "Cream of Mushroom": "كريم الفطر",
    "Garlic Cream": "كريم الثوم",
    "Onion Cream": "كريم البصل",
    "Sweet Corn": "ذرة حلوة",
    "Caramel": "كراميل",
    "Derby": "ديربي",
    "Japanese": "ياباني",
    "French Cheese": "جبنة فرنسية",
    "Thyme": "زعتر",
    "Tomato": "طماطم",
    "Labneh & Herbs": "لبنة وأعشاب",
    "Olives": "زيتون",
    "Curry Flavor": "نكهة كاري",
    "Mixed Spices": "توابل مشكلة",
    "Seven Spices": "سبع بهارات",
    "Kabsa Spices": "بهارات الكبسة",
    "Biryani Spices": "بهارات البرياني",
    "Mandi Spices": "بهارات المندي",
    "Chicken Stock Powder": "بودرة مرق الدجاج",
    "Meat Stock Powder": "بودرة مرق اللحم",
    "French Fries Potato Seasoning": "بهارات بطاطا مقلية",
    "Ketchup Seasoning": "بهارات كتشب",
    "Hot Seasoning": "بهار حار",
    "Noodle Flavors": "نكهات النودلز",
    "Vegetable Flavor": "نكهة الخضار",
    "Chicken Flavor": "نكهة دجاج",
    "Chicken with Curry Flavor": "نكهة دجاج بالكاري",
    "Teriyaki Flavor": "نكهة تيراياكي",
    "Fried Noodles Flavor": "نكهة الشعيرية المقلية",
    "Mortadella Spices": "بهارات المرتديلا",
    "Original Mortadella": "مرتديلا اورجينال",
    "Smoked Flavor": "بهارات مرتديلا بنكهة مدخن",
    "Pizza Flavor": "بهارات مرتديلا بنكهة بيتزا",
    "Olive Flavor": "بهارات مرتديلا بنكهة الزيتون",
    "Mushroom Flavor": "بهارات مرتديلا بنكهة الفطر",
    "Barbecue Flavor": "بهارات المرتديلا بنكهة الباربيكيو",
    "Red Pepper Flavor": "بهارات المرتديلا بنكهة الفليفلة الحمراء",
    "Mixed Sauces": "صوصات مشكلة",
    "Barbecue Sauce": "صوص الباربيكيو",
    "Buffalo Sauce": "صوص البوفالو",
    "Salty Soy Sauce": "صوص الصويا المالح",
    "Sweet Soy Sauce": "صوص الصويا الحلو",
    "Hot Sauce": "صوص الشطة",
    "Muhammara Sauce": "صلصة المحمرة",
    "Mayonnaise": "صوص المايونيز",
    "Caramel Syrup": "قطر الكراميل",
    "Fast Food Seasonings": "بهارات الوجبات السريعة",
    "Chicken Seasoning (Broasted, Grilled, Strips)": "بهارات الفروج (بروستد، مشوي، مسحب)",
    "Shawarma Seasoning (Beef, Chicken)": "بهارات الشاورما (لحم، دجاج)",
    "Crispy Seasoning": "بهارات الكريسبي",
    "Hamburger Seasoning (Beef, Chicken)": "بهارات الهمبرغر (لحم، دجاج)",
    "Kebab Seasoning": "بهارات الكباب",
    "Shish Tawook Seasoning": "بهارات الشيش طاووق",
    "Fajita Spices": "بهارات فاهيتا",

}

# Strings that are demo leftovers or deliberately untranslated (brand names,
# email, phone, numerals). Listing them here keeps them out of the
# "missing translation" report.
SKIP = {
    "info@takwafoods.com", "+963 961111231", "+963 942002287",
    "30+", "225+", "160+", "170+",
    # the stat numbers are now split from their "+" so the counter can
    # animate just the digits; the bare numerals need no translation
    "30", "225", "160", "170",
    # the header toggle names the language you are reading; on an Arabic
    # page it is set to العربية before the text pass runs, so it is already
    # in the target language and must not be reported as untranslated
    "العربية",
    # decorative initials on the team cards that have no photograph
    "AS", "ZE", "1996", "2007", "2013", "2014", "2025",
    "(1)", "Renault", "Takwa Foods",
    # known demo content still on the site, tracked separately
    "Product Full Name", "asfdasda", "sarah mitchell", "atitle", "type",
    "title", "translate.Careers", "Blog Title 01", "Blog Title 02",
    "Lorem ipsum dolor sit amet consectetur adipisicing elit. Sequi, hic fuga. "
    "Est qui eaque sint sit ipsa voluptatum adipisci",
    "MIXED SPICES", "a2", "cheese", "ketchup", "chilli",
    "2025-06-28", "2026-09-01", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    # pack sizes read the same in both languages
    "6x80g", "6x68g", "12x20g", "50g", "50x2g",
}

# Blog tags and the placeholder article bodies on the two leftover demo posts.
# They are skipped rather than translated because the English pages are still
# demo content themselves.
SKIP |= {t for t in (
    "#car", "#car rent", "#car sale", "#car repair", "#car listing",
    "#listing", "#listing car", "#rent car", "#sale car",
    "#tag1", "#tag2", "#tag3", "#tag4",
)}
_LOREM_PREFIXES = ("Lorem ipsum", "Quo id nemore", "Unum melius option",
                   "Consetetur definitionem", "Ut qui eligendi",
                   "Nec in rebum", "Eu suavitate contentiones",
                   "Embark on a delectable journey")


def is_placeholder(text):
    """True for demo copy still sitting on the English site."""
    return text.startswith(_LOREM_PREFIXES)


# --------------------------------------------------------------- overrides --
# Edits made in the Arabic text index (_text-index.html) are kept in a JSON
# file beside this one rather than written back into the table above.
#
# The table is hand-written Python with comments grouping it by area of the
# site; a program editing it in place would have to preserve all of that, and
# one bad rewrite would take the whole translation set with it. A separate
# overrides file cannot corrupt the original, is obvious in a diff, and can be
# deleted wholesale to get back to the authored text.
#
# Overrides are applied last, so an entry here always wins.
OVERRIDES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "translations_ar_overrides.json")


def load_overrides():
    try:
        with open(OVERRIDES_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return {}
    except (ValueError, OSError) as exc:
        # a broken overrides file must not take the site's Arabic down with it
        print("  !! ignoring %s: %s" % (os.path.basename(OVERRIDES_PATH), exc))
        return {}
    return {k: v for k, v in data.items() if isinstance(v, str) and v.strip()}


# A copy of the table as written in this file, taken before any override is
# applied. Reverting an edit needs the original back, and once AR has been
# updated the only other way to recover it is to re-read the module.
AUTHORED = dict(AR)

OVERRIDES = load_overrides()
AR.update(OVERRIDES)


def load_authored():
    """The translations as authored here, ignoring any override."""
    return AUTHORED
