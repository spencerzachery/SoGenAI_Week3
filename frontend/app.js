// RAG & Prompt Engineering Lab - Application Logic

let currentMode = 'compare';
let currentTab = 'rag';

// =============================================================================
// Prompt Templates for RAG Playground
// =============================================================================
const PROMPT_TEMPLATES = {
    'default': 'You are an AWS support specialist. Provide accurate, helpful responses.',
    'zero-shot': 'You are an AWS Enterprise Support specialist. Answer the question directly and concisely. Provide specific, actionable guidance.',
    'few-shot': `You are an AWS Enterprise Support specialist. Follow this response pattern:

Example Q: How do I reset my password?
Example A: To reset your AWS console password:
1. Go to the AWS sign-in page
2. Click "Forgot password"
3. Enter your email address
4. Follow the reset link sent to your email

Now answer the user's question using the same structured format with numbered steps.`,
    'chain-of-thought': `You are an AWS Enterprise Support specialist. Think through problems step by step:

1. UNDERSTAND: First, identify what the user is asking
2. ANALYZE: Consider possible causes or solutions
3. RECOMMEND: Provide a structured response with clear steps
4. REFERENCE: Include relevant AWS documentation or best practices

Show your reasoning process before providing the final answer.`,
    'tam-role': `You are a Technical Account Manager (TAM) at AWS Enterprise Support with 10+ years of experience.

Your approach:
- Build relationships and provide proactive guidance
- Focus on business outcomes, not just technical solutions
- Reference the Well-Architected Framework when relevant
- Suggest optimization opportunities
- Consider the customer's broader architecture

Respond professionally but warmly, as you would to a valued customer.`,
    'sa-role': `You are a Senior AWS Solutions Architect specializing in enterprise architectures.

Your focus areas:
- Architectural best practices and patterns
- Scalability and high availability
- Reliability and fault tolerance
- Cost optimization strategies
- Security best practices

When applicable, provide multiple options with trade-offs so the customer can make informed decisions.`,
    'custom': ''
};


// =============================================================================
// Prompt Engineering Lab Templates (More Detailed)
// =============================================================================
const PE_TEMPLATES = {
    'zero-shot': {
        name: 'Zero-Shot',
        description: 'Direct instruction without examples. Tests the model\'s base knowledge and ability to follow instructions.',
        tips: [
            'Be clear and specific in your instructions',
            'Works well for straightforward questions',
            'May lack consistency in output format'
        ],
        prompt: `You are an AWS support specialist. Answer the following question directly and concisely.

Question: {query}

Answer:`
    },
    'few-shot': {
        name: 'Few-Shot',
        description: 'Provide examples to guide the model\'s response format, style, and level of detail.',
        tips: [
            'Use 2-3 high-quality examples',
            'Examples should match desired output format',
            'Great for consistent formatting'
        ],
        prompt: `You are an AWS support specialist. Answer questions following this format:

Example Question: How do I check my EC2 instance status?
Example Answer:
**Issue**: Checking EC2 instance status
**Steps**:
1. Open the EC2 console at https://console.aws.amazon.com/ec2/
2. In the navigation pane, choose "Instances"
3. Select your instance and view the "Status check" column
4. For detailed checks, select the instance and choose the "Status checks" tab
**Additional Info**: Status checks run every minute and report pass/fail status.

Example Question: How do I enable CloudWatch detailed monitoring?
Example Answer:
**Issue**: Enabling detailed monitoring for EC2
**Steps**:
1. Open the EC2 console
2. Select the instance(s) you want to monitor
3. Choose Actions → Monitor and troubleshoot → Manage detailed monitoring
4. Select "Enable" and confirm
**Additional Info**: Detailed monitoring provides 1-minute metrics (vs 5-minute for basic). Additional charges apply.

Now answer this question using the same format:
Question: {query}

Answer:`
    },
    'chain-of-thought': {
        name: 'Chain-of-Thought',
        description: 'Encourages step-by-step reasoning, improving accuracy for complex problems.',
        tips: [
            'Best for troubleshooting and analysis',
            'Shows reasoning process',
            'Helps catch logical errors'
        ],
        prompt: `You are an AWS support specialist. Think through this problem step by step.

Question: {query}

Let's approach this systematically:

**Step 1 - Understand the Problem:**
First, let me identify exactly what is being asked...

**Step 2 - Gather Context:**
The relevant AWS services and concepts involved are...

**Step 3 - Analyze Possible Causes/Solutions:**
Considering the situation, the possible approaches are...

**Step 4 - Recommend Solution:**
Based on my analysis, here is my recommendation...

**Step 5 - Additional Considerations:**
Other things to keep in mind...`
    },
    'role-tam': {
        name: 'Role: TAM',
        description: 'Assigns a Technical Account Manager persona for customer-focused, relationship-driven responses.',
        tips: [
            'Focuses on business outcomes',
            'Proactive and consultative tone',
            'References Well-Architected Framework'
        ],
        prompt: `You are a Technical Account Manager (TAM) at AWS Enterprise Support with 10+ years of experience helping enterprise customers.

Your communication style:
- Professional yet warm and approachable
- Focus on business outcomes, not just technical details
- Proactive in identifying optimization opportunities
- Reference the AWS Well-Architected Framework when relevant
- Consider the customer's broader architecture and goals

Customer Question: {query}

As their TAM, provide a thoughtful response that addresses both the immediate question and any related considerations that would benefit their AWS journey.`
    },
    'role-sa': {
        name: 'Role: Solutions Architect',
        description: 'Assigns a Solutions Architect persona for architecture-focused, technical responses.',
        tips: [
            'Deep technical expertise',
            'Presents multiple options with trade-offs',
            'Focuses on best practices'
        ],
        prompt: `You are a Senior AWS Solutions Architect specializing in enterprise cloud architectures.

Your expertise includes:
- Designing highly available and scalable systems
- Security best practices and compliance
- Cost optimization strategies
- Migration and modernization patterns
- Multi-account and multi-region architectures

Question: {query}

Provide an architecture-focused response. When applicable, present multiple options with their trade-offs so the customer can make an informed decision based on their specific requirements.`
    },
    'structured-json': {
        name: 'Structured: JSON',
        description: 'Requests output in JSON format for programmatic processing.',
        tips: [
            'Great for automation and parsing',
            'Define the schema clearly',
            'Useful for consistent data extraction'
        ],
        prompt: `You are an AWS support specialist. Answer the following question and format your response as a JSON object.

Question: {query}

Respond with a JSON object containing these fields:
{
  "summary": "Brief one-line summary of the answer",
  "category": "The AWS service category (e.g., Compute, Storage, Networking)",
  "steps": ["Array of step-by-step instructions"],
  "services_involved": ["List of AWS services mentioned"],
  "estimated_time": "Estimated time to complete (e.g., '5-10 minutes')",
  "difficulty": "Easy/Medium/Hard",
  "documentation_links": ["Relevant AWS documentation URLs"],
  "warnings": ["Any important warnings or considerations"]
}

JSON Response:`
    },
    'structured-list': {
        name: 'Structured: Numbered List',
        description: 'Requests a clear, numbered list format for easy scanning.',
        tips: [
            'Easy to follow and reference',
            'Good for procedures and checklists',
            'Clear action items'
        ],
        prompt: `You are an AWS support specialist. Answer the following question using a clear, numbered list format.

Question: {query}

Format your response as follows:

**Summary:** [One sentence summary]

**Prerequisites:**
1. [First prerequisite]
2. [Second prerequisite]
...

**Steps:**
1. [First step with clear action]
2. [Second step with clear action]
...

**Verification:**
1. [How to verify step 1 worked]
2. [How to verify step 2 worked]
...

**Common Issues:**
- [Issue 1]: [Solution]
- [Issue 2]: [Solution]

**Next Steps:** [What to do after completing this task]`
    },
    'self-consistency': {
        name: 'Self-Consistency',
        description: 'Asks the model to verify and refine its own answer for improved accuracy.',
        tips: [
            'Reduces errors and hallucinations',
            'Good for critical decisions',
            'Model checks its own work'
        ],
        prompt: `You are an AWS support specialist. Answer the following question, then verify your answer.

Question: {query}

**Initial Answer:**
[Provide your initial response to the question]

**Verification Check:**
Now, review your answer and check for:
1. Technical accuracy - Are all AWS service names, features, and behaviors correct?
2. Completeness - Did you address all aspects of the question?
3. Best practices - Does your answer follow AWS recommended practices?
4. Potential issues - Are there any edge cases or warnings to mention?

**Refined Answer:**
Based on your verification, provide your final, refined answer. If your initial answer was correct, confirm it. If you found any issues, correct them here.`
    }
};

// =============================================================================
// Technique Information
// =============================================================================
const TECHNIQUE_INFO = {
    'zero-shot': {
        title: '🎯 Zero-Shot Prompting',
        description: 'Zero-shot prompting provides instructions without examples. The model relies entirely on its training to understand and respond to the task.',
        whenToUse: [
            'Simple, straightforward questions',
            'When you want to test base model capabilities',
            'Quick queries where format doesn\'t matter much'
        ],
        limitations: [
            'Output format may be inconsistent',
            'May not follow specific style requirements',
            'Less reliable for complex tasks'
        ]
    },
    'few-shot': {
        title: '📚 Few-Shot Prompting',
        description: 'Few-shot prompting includes examples that demonstrate the desired output format and style. The model learns the pattern from examples.',
        whenToUse: [
            'When you need consistent output format',
            'For domain-specific terminology or style',
            'When examples clarify ambiguous instructions'
        ],
        limitations: [
            'Uses more tokens (higher cost)',
            'Examples must be high quality',
            'May overfit to example patterns'
        ]
    },
    'chain-of-thought': {
        title: '🔗 Chain-of-Thought Prompting',
        description: 'Chain-of-thought prompting encourages the model to show its reasoning process step by step, improving accuracy on complex problems.',
        whenToUse: [
            'Complex troubleshooting scenarios',
            'Multi-step problem solving',
            'When you need to understand the reasoning'
        ],
        limitations: [
            'Longer responses (more tokens)',
            'May be overkill for simple questions',
            'Reasoning can sometimes be circular'
        ]
    },
    'role-based': {
        title: '🎭 Role-Based Prompting',
        description: 'Role-based prompting assigns a specific persona or expertise to the model, shaping its knowledge focus, tone, and perspective.',
        whenToUse: [
            'When specific expertise is needed',
            'To match communication style to audience',
            'For consistent persona across conversations'
        ],
        limitations: [
            'Role may not perfectly match expectations',
            'Can introduce biases from the role',
            'May conflict with other instructions'
        ]
    },
    'structured-output': {
        title: '📋 Structured Output Prompting',
        description: 'Structured output prompting requests responses in specific formats like JSON, lists, or tables for easier parsing and consistency.',
        whenToUse: [
            'When output needs to be parsed programmatically',
            'For consistent documentation format',
            'When creating checklists or procedures'
        ],
        limitations: [
            'May truncate content to fit format',
            'JSON output may have syntax errors',
            'Less natural conversational flow'
        ]
    },
    'self-consistency': {
        title: '✅ Self-Consistency Prompting',
        description: 'Self-consistency prompting asks the model to verify and potentially correct its own answer, reducing errors and hallucinations.',
        whenToUse: [
            'Critical decisions or recommendations',
            'When accuracy is paramount',
            'Complex technical questions'
        ],
        limitations: [
            'Doubles response length and cost',
            'Model may not catch all errors',
            'Can be overly cautious'
        ]
    }
};


// =============================================================================
// Initialization
// =============================================================================
document.addEventListener('DOMContentLoaded', () => {
    // Check for auto-populated KB ID from config
    if (typeof DEFAULT_KB_ID !== 'undefined' && DEFAULT_KB_ID && DEFAULT_KB_ID !== 'PLACEHOLDER') {
        document.getElementById('kbId').value = DEFAULT_KB_ID;
        showStatus('Knowledge Base ID auto-populated from deployment', 'success');
    } else {
        const savedKbId = localStorage.getItem('kbId');
        if (savedKbId) {
            document.getElementById('kbId').value = savedKbId;
        }
    }
    
    // Load saved model preference
    const savedModel = localStorage.getItem('modelId');
    if (savedModel) {
        document.getElementById('modelSelect').value = savedModel;
        document.getElementById('peModelSelect').value = savedModel;
    }
    
    // Save KB ID on change
    document.getElementById('kbId').addEventListener('change', (e) => {
        localStorage.setItem('kbId', e.target.value);
    });
    
    // Save model on change
    document.getElementById('modelSelect').addEventListener('change', (e) => {
        localStorage.setItem('modelId', e.target.value);
        document.getElementById('peModelSelect').value = e.target.value;
    });
    
    document.getElementById('peModelSelect').addEventListener('change', (e) => {
        localStorage.setItem('modelId', e.target.value);
        document.getElementById('modelSelect').value = e.target.value;
    });
    
    // Enter key to submit
    document.getElementById('queryInput').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) submitQuery();
    });
    
    document.getElementById('peQueryInput').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) submitPromptComparison();
    });
    
    // Initialize prompt editor and previews
    updatePromptPreview();
    updatePromptAPreview();
    updatePromptBPreview();
});

// =============================================================================
// Tab Navigation
// =============================================================================
function switchTab(tab) {
    currentTab = tab;
    
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tab + 'Tab').classList.add('active');
}


// =============================================================================
// Status and UI Helpers
// =============================================================================
function showStatus(message, type = 'success', elementId = 'statusBar') {
    const statusBar = document.getElementById(elementId);
    statusBar.textContent = message;
    statusBar.className = 'status-bar' + (type === 'warning' ? ' warning' : '');
    statusBar.style.display = 'block';
    setTimeout(() => { statusBar.style.display = 'none'; }, 5000);
}

function setMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });
    
    const ragCard = document.getElementById('ragCard');
    const directCard = document.getElementById('directCard');
    const resultsSection = document.getElementById('resultsSection');
    
    if (mode === 'rag') {
        ragCard.classList.remove('hidden');
        directCard.classList.add('hidden');
        resultsSection.classList.add('single-column');
    } else if (mode === 'direct') {
        ragCard.classList.add('hidden');
        directCard.classList.remove('hidden');
        resultsSection.classList.add('single-column');
    } else {
        ragCard.classList.remove('hidden');
        directCard.classList.remove('hidden');
        resultsSection.classList.remove('single-column');
    }
}

function updatePromptPreview() {
    const style = document.getElementById('promptStyle').value;
    const editor = document.getElementById('promptEditor');
    if (style !== 'custom') {
        editor.value = PROMPT_TEMPLATES[style];
    }
}

function togglePromptEditor() {
    const container = document.getElementById('promptEditorContainer');
    const chevron = document.getElementById('promptChevron');
    container.classList.toggle('expanded');
    chevron.classList.toggle('rotated');
}

function resetPrompt() {
    const style = document.getElementById('promptStyle').value;
    document.getElementById('promptEditor').value = PROMPT_TEMPLATES[style === 'custom' ? 'default' : style];
}

function copyPrompt() {
    navigator.clipboard.writeText(document.getElementById('promptEditor').value).then(() => {
        showStatus('Prompt copied to clipboard!', 'success');
    });
}

function setQuery(text, tab = 'rag') {
    const inputId = tab === 'rag' ? 'queryInput' : 'peQueryInput';
    document.getElementById(inputId).value = text.trim();
    document.getElementById(inputId).focus();
}

function clearResults() {
    document.getElementById('ragResult').textContent = 'Results will appear here after submitting a query...';
    document.getElementById('directResult').textContent = 'Results will appear here after submitting a query...';
    document.getElementById('ragCitations').style.display = 'none';
    document.getElementById('queryInput').value = '';
}


// =============================================================================
// RAG Playground Functions
// =============================================================================
async function submitQuery() {
    const query = document.getElementById('queryInput').value.trim();
    const kbId = document.getElementById('kbId').value.trim();
    const modelId = document.getElementById('modelSelect').value;
    const systemPrompt = document.getElementById('promptEditor').value.trim();
    
    if (!query) {
        showStatus('Please enter a query', 'warning');
        return;
    }
    
    if ((currentMode === 'rag' || currentMode === 'compare') && !kbId) {
        showStatus('Please enter your Knowledge Base ID for RAG queries', 'warning');
        return;
    }
    
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.textContent = '⏳ Processing...';
    
    if (currentMode === 'rag' || currentMode === 'compare') {
        document.getElementById('ragResult').innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    }
    if (currentMode === 'direct' || currentMode === 'compare') {
        document.getElementById('directResult').innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    }
    document.getElementById('ragCitations').style.display = 'none';
    
    try {
        const promises = [];
        
        if (currentMode === 'rag' || currentMode === 'compare') {
            promises.push(callApi(query, true, kbId, modelId, systemPrompt));
        } else {
            promises.push(Promise.resolve(null));
        }
        
        if (currentMode === 'direct' || currentMode === 'compare') {
            promises.push(callApi(query, false, null, modelId, systemPrompt));
        } else {
            promises.push(Promise.resolve(null));
        }
        
        const [ragResponse, directResponse] = await Promise.all(promises);
        
        if (ragResponse) {
            displayResult('ragResult', ragResponse);
            if (ragResponse.citations && ragResponse.citations.length > 0) {
                displayCitations(ragResponse.citations);
            }
        }
        
        if (directResponse) {
            displayResult('directResult', directResponse);
        }
        
    } catch (error) {
        console.error('Error:', error);
        const errorMsg = `Error: ${error.message}`;
        if (currentMode === 'rag' || currentMode === 'compare') {
            document.getElementById('ragResult').textContent = errorMsg;
        }
        if (currentMode === 'direct' || currentMode === 'compare') {
            document.getElementById('directResult').textContent = errorMsg;
        }
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = '🚀 Submit Query';
    }
}

async function callApi(query, useRag, kbId, modelId, systemPrompt) {
    const response = await fetch(`${API_ENDPOINT}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query: query,
            useRag: useRag,
            knowledgeBaseId: kbId,
            modelId: modelId,
            systemPrompt: systemPrompt
        })
    });
    
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error: ${response.status} - ${errorText}`);
    }
    
    return await response.json();
}


function displayResult(elementId, response) {
    const element = document.getElementById(elementId);
    
    if (response.error) {
        element.textContent = `Error: ${response.error}`;
        return;
    }
    
    let html = response.response
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/`(.*?)`/g, '<code style="background:#0d0d1a;padding:2px 6px;border-radius:4px;">$1</code>')
        .replace(/^(\d+)\./gm, '<strong>$1.</strong>');
    
    element.innerHTML = `<p>${html}</p>`;
}

function displayCitations(citations) {
    const container = document.getElementById('citationsList');
    container.innerHTML = '';
    
    citations.forEach((citation, index) => {
        const div = document.createElement('div');
        div.className = 'citation-item';
        const filename = citation.uri ? citation.uri.split('/').pop() : 'Unknown source';
        const preview = citation.text ? citation.text.substring(0, 150) + '...' : '';
        div.innerHTML = `<strong>[${index + 1}]</strong> ${filename}${preview ? `<br><small style="color:#666">${preview}</small>` : ''}`;
        container.appendChild(div);
    });
    
    document.getElementById('ragCitations').style.display = 'block';
}

// =============================================================================
// Prompt Engineering Lab Functions
// =============================================================================
function selectTechnique(technique) {
    // Update selected card
    document.querySelectorAll('.technique-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.getElementById('tech-' + technique).classList.add('selected');
    
    // Update technique info
    const info = TECHNIQUE_INFO[technique];
    if (info) {
        document.getElementById('techniqueInfo').innerHTML = `
            <h4>${info.title}</h4>
            <p>${info.description}</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 12px;">
                <div>
                    <strong style="color: #00c853;">✓ When to Use:</strong>
                    <ul>${info.whenToUse.map(item => `<li>${item}</li>`).join('')}</ul>
                </div>
                <div>
                    <strong style="color: #ff9800;">⚠ Limitations:</strong>
                    <ul>${info.limitations.map(item => `<li>${item}</li>`).join('')}</ul>
                </div>
            </div>
        `;
    }
    
    // Map technique to dropdown values
    const techniqueMap = {
        'zero-shot': 'zero-shot',
        'few-shot': 'few-shot',
        'chain-of-thought': 'chain-of-thought',
        'role-based': 'role-tam',
        'structured-output': 'structured-list',
        'self-consistency': 'self-consistency'
    };
    
    // Set dropdown A to zero-shot and B to selected technique for comparison
    document.getElementById('promptASelect').value = 'zero-shot';
    document.getElementById('promptBSelect').value = techniqueMap[technique] || technique;
    
    updatePromptAPreview();
    updatePromptBPreview();
}


function updatePromptAPreview() {
    const technique = document.getElementById('promptASelect').value;
    const template = PE_TEMPLATES[technique];
    if (template) {
        document.getElementById('promptAPreview').textContent = template.prompt.replace('{query}', '[Your question here]');
    }
}

function updatePromptBPreview() {
    const technique = document.getElementById('promptBSelect').value;
    const template = PE_TEMPLATES[technique];
    if (template) {
        document.getElementById('promptBPreview').textContent = template.prompt.replace('{query}', '[Your question here]');
    }
}

function clearPromptResults() {
    document.getElementById('promptAResult').textContent = 'Results will appear here...';
    document.getElementById('promptBResult').textContent = 'Results will appear here...';
    document.getElementById('peQueryInput').value = '';
}

async function submitPromptComparison() {
    const query = document.getElementById('peQueryInput').value.trim();
    const modelId = document.getElementById('peModelSelect').value;
    
    if (!query) {
        showStatus('Please enter a question to compare', 'warning', 'peStatusBar');
        return;
    }
    
    const submitBtn = document.getElementById('peSubmitBtn');
    submitBtn.disabled = true;
    submitBtn.textContent = '⏳ Comparing...';
    
    document.getElementById('promptAResult').innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    document.getElementById('promptBResult').innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    
    try {
        const techniqueA = document.getElementById('promptASelect').value;
        const techniqueB = document.getElementById('promptBSelect').value;
        
        const promptA = PE_TEMPLATES[techniqueA].prompt.replace('{query}', query);
        const promptB = PE_TEMPLATES[techniqueB].prompt.replace('{query}', query);
        
        const [responseA, responseB] = await Promise.all([
            callApi(query, false, null, modelId, promptA),
            callApi(query, false, null, modelId, promptB)
        ]);
        
        displayResult('promptAResult', responseA);
        displayResult('promptBResult', responseB);
        
    } catch (error) {
        console.error('Error:', error);
        const errorMsg = `Error: ${error.message}`;
        document.getElementById('promptAResult').textContent = errorMsg;
        document.getElementById('promptBResult').textContent = errorMsg;
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = '🚀 Compare Techniques';
    }
}
