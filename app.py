<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> The Political Fact-Checker</title>
    <!-- Load Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Load Inter font -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
        /* Simple spinner animation */
        .spinner {
           # border: 4px solid rgba(0, 0, 0, 0.1);
            border-left-color: #4f46e5;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to {
                transform: rotate(360deg);
            }
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center p-4">

    <div class="bg-white p-8 rounded-2xl shadow-xl w-full max-w-2xl border border-gray-200">
        <!-- Header -->
        <div class="text-center mb-6">
            <h1 class="text-3xl font-bold text-gray-800">🏛️ The Political Fact-Checker</h1>
            <p class="text-gray-600 mt-2">
                Enter any specific political statement, quote, or claim below. This tool acts as an impartial analyst,
                using real-time Google Search to verify the claim and provide a balanced summary.
            </p>
        </div>

        <!-- Form -->
        <form id="checker-form" class="space-y-6">
            <div>
                <label for="claim-input" class="block text-sm font-medium text-gray-700 mb-1">
                    Enter a Specific Political Claim:
                </label>
                <textarea id="claim-input" rows="4" class="w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition" placeholder="e.g., 'Candidate X said they would cut taxes for 90% of families.'"></textarea>
            </div>
            
            <div>
                <label for="context-input" class="block text-sm font-medium text-gray-700 mb-1">
                    Location / Context (Recommended):
                </label>
                <input type="text" id="context-input" class="w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition" placeholder="e.g., 'California 2024', 'UK general election'">
                <p class="text-xs text-gray-500 mt-1">Providing location or context (like a state or year) helps verify local or time-specific claims.</p>
            </div>

            <button type_button="submit" id="verify-button" class="w-full bg-indigo-600 text-white font-semibold py-3 px-6 rounded-lg shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition duration-200 ease-in-out flex items-center justify-center">
                <span id="button-text">Verify Claim</span>
                <div id="loading-spinner" class="spinner ml-3 hidden"></div>
            </button>
        </form>

        <!-- Error Message -->
        <div id="error-message" class="hidden mt-6 p-4 bg-red-100 text-red-700 border border-red-300 rounded-lg">
            <!-- Error content will be set by JS -->
        </div>

        <!-- Verification Report -->
        <div id="results-container" class="hidden mt-8 pt-6 border-t border-gray-200">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">✅ Verification Report</h2>
            
            <!-- Summary Section -->
            <h3 class="text-lg font-semibold text-gray-700 mb-2">Summary</h3>
            <div id="report-summary" class="prose prose-indigo max-w-none text-gray-600 bg-gray-50 p-4 rounded-lg border">
                <!-- Summary will be populated here -->
            </div>

            <!-- Sources Section -->
            <h3 class="text-lg font-semibold text-gray-700 mt-6 mb-2">Sources</h3>
            <ul id="report-sources" class="list-disc list-inside space-y-2">
                <!-- Sources will be populated here -->
            </ul>
        </div>
    </div>

    <script>
        const form = document.getElementById('checker-form');
        const claimInput = document.getElementById('claim-input');
        const contextInput = document.getElementById('context-input');
        const verifyButton = document.getElementById('verify-button');
        const buttonText = document.getElementById('button-text');
        const loadingSpinner = document.getElementById('loading-spinner');
        const errorMessage = document.getElementById('error-message');
        const resultsContainer = document.getElementById('results-container');
        const reportSummary = document.getElementById('report-summary');
        const reportSources = document.getElementById('report-sources');

        // This is the model to use.
        const MODEL_NAME = 'gemini-2.5-flash-preview-09-2025';
        
        // --- IMPORTANT ---
        // Leave the API key as an empty string.
        // The Canvas environment will automatically provide the necessary authentication.
        const API_KEY = '';
        // --- ----------- ---

        const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL_NAME}:generateContent?key=${API_KEY}`;

        // System instruction to guide the AI's behavior
        const SYSTEM_INSTRUCTION = `
            You are an impartial, neutral political fact-checker. Your sole purpose is to analyze a given political claim using Google Search results.
            You must not take a personal stance or express any opinion.
            Your response must be structured as follows:
            1.  **Verdict:** State clearly whether the claim is True, False, Misleading, Lacks Context, or Unverifiable, based *only* on the provided search results.
            2.  **Analysis:** Provide a concise, balanced summary of the facts found in the search results. Present evidence that supports the claim and evidence that contradicts it, if both exist.
            3.  **Conclusion:** Briefly explain why you reached your verdict, citing the key findings from the search.
            
            You must be objective and stick strictly to the information available in the search results. Do not add any information not present in the sources.
            If the claim is too vague or lacks sufficient information from search to verify, state that it is "Unverifiable" and explain what information is missing.
        `;
        
        // Listen for form submission
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const claim = claimInput.value;
            const context = contextInput.value;

            if (!claim) {
                displayError("Please enter a political claim to verify.");
                return;
            }

            // Combine claim and context for a better query
            const userQuery = `
                Political Claim: "${claim}"
                Context: "${context || 'No context provided'}"
                
                Please fact-check this claim based on the system instruction.
            `;

            // Update UI to show loading state
            setLoading(true);
            hideError();
            resultsContainer.classList.add('hidden');

            try {
                // Construct the payload for the API
                const payload = {
                    contents: [{ parts: [{ text: userQuery }] }],
                    tools: [{ "google_search": {} }], // Enable Google Search grounding
                    systemInstruction: {
                        parts: [{ text: SYSTEM_INSTRUCTION }]
                    },
                };

                // Call the API with retry logic
                const response = await fetchWithRetry(API_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    const errorBody = await response.json();
                    throw new Error(`API Error: ${response.status} ${response.statusText}. ${errorBody?.error?.message || ''}`);
                }

                const result = await response.json();
                
                const candidate = result.candidates?.[0];
                const text = candidate?.content?.parts?.[0]?.text;
                const groundingMetadata = candidate?.groundingMetadata;

                if (!text) {
                    throw new Error("No valid text response received from the model.");
                }
                
                // Process and display the results
                displayResults(text, groundingMetadata);

            } catch (error) {
                console.error('Fact-checking failed:', error);
                displayError(`Failed to verify claim. ${error.message}`);
            } finally {
                // Restore UI from loading state
                setLoading(false);
            }
        });

        /**
         * Fetches a resource with exponential backoff.
         * @param {string} url - The URL to fetch.
         * @param {object} options - The fetch options.
         * @param {number} maxRetries - Maximum number of retries.
         * @param {number} baseDelay - Base delay in ms for backoff.
         */
        async function fetchWithRetry(url, options, maxRetries = 5, baseDelay = 1000) {
            let attempt = 0;
            while (attempt < maxRetries) {
                try {
                    const response = await fetch(url, options);
                    // Check for specific retryable errors if needed, e.g., 429, 503
                    if (!response.ok && (response.status === 429 || response.status >= 500)) {
                         throw new Error(`Retryable error: ${response.status}`);
                    }
                    return response; // Success
                } catch (error) {
                    attempt++;
                    if (attempt >= maxRetries) {
                        throw error; // Max retries reached
                    }
                    const delay = baseDelay * Math.pow(2, attempt - 1);
                    // Don't log to console, as per instructions
                    // console.log(`Attempt ${attempt} failed. Retrying in ${delay}ms...`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            }
        }
        
        /**
         * Displays the fact-checking results in the UI.
         * @param {string} summaryText - The summary text from the model.
         * @param {object} groundingMetadata - The metadata containing sources.
         */
        function displayResults(summaryText, groundingMetadata) {
            // Sanitize and format summary text (replace newlines with <br>)
            reportSummary.innerHTML = summaryText.replace(/\n/g, '<br>');

            // Clear old sources
            reportSources.innerHTML = '';
            
            let sources = [];
            if (groundingMetadata && groundingMetadata.groundingAttributions) {
                sources = groundingMetadata.groundingAttributions
                    .map(attr => attr.web)
                    .filter(web => web && web.uri && web.title); // Filter out invalid sources
            }

            if (sources.length > 0) {
                // Create unique sources
                const uniqueSources = new Map();
                sources.forEach(source => {
                    if (!uniqueSources.has(source.uri)) {
                        uniqueSources.set(source.uri, source.title);
                    }
                });

                uniqueSources.forEach((title, uri) => {
                    const li = document.createElement('li');
                    const a = document.createElement('a');
                    a.href = uri;
                    a.textContent = title || uri; // Use title, fall back to URI
                    a.target = '_blank'; // Open in new tab
                    a.rel = 'noopener noreferrer';
                    a.className = 'text-indigo-600 hover:text-indigo-800 hover:underline break-words';
                    li.appendChild(a);
                    reportSources.appendChild(li);
                });
            } else {
                reportSources.innerHTML = '<li>No supporting sources were cited by the model.</li>';
            }

            resultsContainer.classList.remove('hidden');
        }

        /**
         * Sets the loading state of the UI.
         * @param {boolean} isLoading - Whether to show the loading state.
         */
        function setLoading(isLoading) {
            if (isLoading) {
                verifyButton.disabled = true;
                buttonText.textContent = 'Verifying...';
                loadingSpinner.classList.remove('hidden');
            } else {
                verifyButton.disabled = false;
                buttonText.textContent = 'Verify Claim';
                loadingSpinner.classList.add('hidden');
            }
        }

        /**
         * Displays an error message in the UI.
         * @param {string} message - The error message to display.
         */
        function displayError(message) {
            errorMessage.textContent = message;
            errorMessage.classList.remove('hidden');
        }

        /**
         * Hides the error message box.
         */
        function hideError() {
            errorMessage.classList.add('hidden');
        }
    </script>
</body>
</html>
