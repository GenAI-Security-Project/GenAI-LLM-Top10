# **OWASP Top 10 for Large Language Model (LLM) Applications Charter**

## **Purpose**

The OWASP Top 10 for Large Language Model Applications is the foundational reference for identifying and understanding security risks in software systems that incorporate large language models. Since its initial release, the project has been widely adopted across industry, research, and standards communities as a baseline for reasoning about the risks introduced by generative AI systems.

As the field of generative AI has expanded, so too has the surrounding ecosystem of projects, frameworks, and commercial solutions. The OWASP Generative AI Security Project was formed in part to organize and scale this broader effort. Within that ecosystem, the Top 10 for LLM Applications remains the core, foundational document.

This charter defines the role, scope, and operating principles of the Top 10 for LLM Applications initiative.

## **Mission**

The mission of the OWASP Top 10 for LLM Applications is to provide a clear, practical, and widely accessible framework for understanding the most critical security risks specific to applications built on large language models.

The project aims to:

* Identify and describe the most important classes of vulnerabilities unique to LLM-based systems  
* Provide actionable guidance for developers, architects, and security practitioners  
* Establish a common language for discussing LLM security risks across the industry  
* Serve as a stable foundation upon which related initiatives and deeper frameworks can build

## **Position Within the OWASP GenAI Security Project**

The Top 10 for LLM Applications operates as a core initiative within the broader OWASP Generative AI Security Project.

It is:

* A foundational reference that informs and influences other GenAI initiatives  
* An input into related efforts such as agentic security, red teaming, and evaluation methodologies  
* A stable, widely recognized baseline for organizations adopting generative AI technologies

It is not intended to replace or subsume other initiatives. Instead, it provides the grounding layer upon which more specialized or advanced work can be built.

## **Scope**

The Top 10 for LLM Applications focuses on security risks that arise specifically from the integration and use of large language models within software systems.

This includes:

* Risks introduced by model behavior, prompting, and output handling  
* Vulnerabilities in application architectures that rely on LLMs  
* Supply chain risks unique to this space

The project intentionally maintains a focused scope. It does not attempt to comprehensively cover all aspects of generative AI risk.

Topics that may be adjacent, but are not the primary focus, include:

* Model safety and alignment  
* Ethical considerations  
* General AI governance frameworks

These areas may be referenced where they intersect directly with security risks, but are not the central domain of this project.

### Relationship to Agentic Security

The OWASP Top 10 for Agentic Applications (ASI) is the peer initiative within the OWASP Generative AI Security Project that addresses risks arising from autonomous AI systems.

The boundary between the two initiatives follows a component-vs-actor distinction:

The Top 10 for LLM Applications covers risks where:

* The model operates as a component within application logic  
* Input processing, output generation, and tool interaction are directed by the application  
* The application retains control over decision-making and execution scope

The Top 10 for Agentic Applications covers risks where:

* The model operates as an autonomous actor with delegated authority  
* The system exercises tool selection, maintains memory, and takes actions with downstream consequences  
* Decision-making extends beyond a single request-response cycle

Where a risk class exists in both contexts, the LLM Top 10 addresses the foundational vulnerability and the Agentic Top 10 addresses the amplified risk introduced by autonomy, persistence, and multi-step execution.

This boundary is intended to:

* Prevent duplication of effort across initiatives  
* Provide contributors and adopters with clear guidance on which list addresses a given concern  
* Allow each initiative to maintain a focused, usable scope

Both initiatives share a common taxonomy and coordinate through the OWASP Generative AI Security Project governance structure.

## **What This Document Is (and Is Not)**

The OWASP Top 10 for LLM Applications is:

* A practical, educational resource designed to raise awareness of key risks  
* A curated set of the most significant and representative vulnerability classes  
* A living document that evolves alongside the technology and threat landscape

It is not:

* A complete or exhaustive taxonomy of all possible vulnerabilities  
* A prescriptive standard or compliance framework  
* A replacement for deeper, specialized guidance provided by other initiatives

The intent is to strike a balance between clarity and completeness, prioritizing usability and impact over exhaustive coverage.

## **Operating Principles**

The Top 10 for LLM Applications initiative is guided by the following principles:

### **1\. Focus on What Is Unique**

The list prioritizes vulnerabilities that are specific to or meaningfully amplified by the use of large language models, rather than general application security issues.

### **2\. Clarity Over Completeness**

Entries are selected and described to maximize understanding and practical value, not to enumerate every possible edge case.

### **3\. Community-Driven Development**

The project is developed through open collaboration with the global OWASP and security community, incorporating input from practitioners, researchers, and industry stakeholders.

### **4\. Stability with Iteration**

While the document evolves over time, updates are made deliberately to preserve continuity and avoid unnecessary churn.

### **5\. Interoperability with the Ecosystem**

The Top 10 is designed to complement, not compete with, other efforts within the OWASP GenAI Security Project and the broader industry.

## **Governance and Alignment**

The Top 10 for LLM Applications initiative operates under the governance framework of the OWASP Generative AI Security Project.

The subteam responsible for this initiative will:

* Organize contributors and working groups for each entry  
* Review and incorporate community feedback  
* Ensure alignment with broader OWASP project governance and standards

Final publication and major decisions will align with the established governance processes of the OWASP GenAI Security Project.

## **Looking Forward**

The field of generative AI continues to evolve rapidly, expanding into areas such as autonomous agents, tool-using systems, and complex multi-model architectures.

As the field expands into autonomous agents and multi-model architectures, the Top 10 for LLM Applications will continue to address foundational model-layer risks while coordinating with peer initiatives such as the OWASP Top 10 for Agentic Applications to ensure comprehensive coverage.

The Top 10 for LLM Applications will continue to evolve alongside these developments while maintaining its core focus: identifying and explaining the most critical security risks inherent to LLM-based applications.

By remaining focused and foundational, the project will continue to serve as a reliable starting point for organizations seeking to build secure generative AI systems.

