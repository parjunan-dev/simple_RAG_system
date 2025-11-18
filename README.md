<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple RAG System (Browser Edition)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Custom scrollbar for text areas */
        textarea::-webkit-scrollbar, .output-scroll::-webkit-scrollbar {
            width: 8px;
        }
        textarea::-webkit-scrollbar-thumb, .output-scroll::-webkit-scrollbar-thumb {
            background-color: #9ca3af;
            border-radius: 4px;
        }
        textarea::-webkit-scrollbar-track, .output-scroll::-webkit-scrollbar-track {
            background-color: #f3f4f6;
        }
        .container-shadow {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
    </style>
</head>
<body class="bg-gray-50 min-h-screen p-4 sm:p-8 font-sans">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-3xl font-extrabold text-gray-900 mb-2">Simple RAG System (Browser)</h1>
        <p class="text-gray-600 mb-6">A beginner-friendly, single-file RAG implementation using JavaScript and the Gemini API.</p>

        <!-- Configuration and Indexing -->
        <div class="bg-white p-6 rounded-xl container-shadow mb-8">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">1. Knowledge Base Input</h2>
            <textarea id="kb-text" rows="10" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 transition duration-150" placeholder="Paste your Knowledge Base text (PDF/MD/TXT content) here. A good size is several paragraphs to a few pages."></textarea>
            
            <div class="flex items-center space-x-4 mt-4 text-sm text-gray-600">
                <p>Chunk Size: <span id="chunk-size-display" class="font-medium text-gray-800">500</span> | Overlap: <span id="overlap-display" class="font-medium text-gray-800">50</span></p>
                <p>Retrieval Top K: <span id="topk-display" class="font-medium text-gray-800">3</span></p>
                <p>LLM: <span class="font-medium text-gray-800">gemini-2.5-flash-preview-09-2025</span></p>
            </div>

            <button onclick="handleBuildIndex()" id="build-index-btn" class="mt-4 w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-lg transition duration-200 disabled:opacity-50" disabled>
                Build Index (Chunk & Embed)
            </button>
            <p id="status-message" class="mt-3 text-sm text-green-600 font-medium"></p>
        </div>

        <!-- Query and Answer -->
        <div class="bg-white p-6 rounded-xl container-shadow">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">2. RAG Query</h2>
            <input type="text" id="query-input" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 transition duration-150 mb-4" placeholder="Ask a question..." disabled>
            
            <button onclick="handleQuery()" id="query-btn" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-200 disabled:opacity-50" disabled>
                Generate Grounded Answer
            </button>
            
            <div id="loading-indicator" class="hidden text-center mt-4">
                <div class="animate-spin inline-block w-6 h-6 border-[3px] border-current border-t-transparent text-blue-600 rounded-full" role="status"></div>
                <p class="text-blue-600 mt-2">Retrieving and Generating...</p>
            </div>

            <div class="mt-6 border-t pt-4">
                <h3 class="text-lg font-medium text-gray-700 mb-2">Retrieved Context (Top 3)</h3>
                <pre id="context-output" class="output-scroll p-3 bg-gray-100 text-gray-700 text-sm rounded-lg whitespace-pre-wrap max-h-40 overflow-y-auto border border-gray-300">Context will appear here after search...</pre>

                <h3 class="text-lg font-medium text-gray-700 mt-4 mb-2">RAG Answer</h3>
                <div id="answer-output" class="output-scroll p-4 bg-indigo-50 text-gray-800 rounded-lg min-h-[100px] border border-indigo-200">
                    The final answer will be generated here.
                </div>
            </div>
        </div>
    </div>

    <script type="module">
        // --- RAG Configuration ---
        const CHUNK_SIZE = 500;
        const CHUNK_OVERLAP = 50;
        const TOP_K = 3;
        const EMBEDDING_DIM = 1536; // Simulate OpenAI embedding dimension
        
        // --- Gemini API Configuration ---
        const GENERATION_MODEL = "gemini-2.5-flash-preview-09-2025";
        const apiKey = ""; // Canvas handles the API key injection

        // --- Global State ---
        let indexStore = []; // Stores { text: string, vector: number[] }

        // --- UI Elements ---
        const kbTextarea = document.getElementById('kb-text');
        const buildBtn = document.getElementById('build-index-btn');
        const queryInput = document.getElementById('query-input');
        const queryBtn = document.getElementById('query-btn');
        const statusMsg = document.getElementById('status-message');
        const loadingIndicator = document.getElementById('loading-indicator');
        const contextOutput = document.getElementById('context-output');
        const answerOutput = document.getElementById('answer-output');

        // Enable/Disable build button based on text area content
        kbTextarea.addEventListener('input', () => {
            buildBtn.disabled = kbTextarea.value.length < 100;
        });


        // --- Utility Functions ---

        /**
         * Simple fixed-size chunking with overlap.
         */
        function chunkText(text) {
            const chunks = [];
            let i = 0;
            while (i < text.length) {
                const chunk = text.substring(i, i + CHUNK_SIZE);
                chunks.push(chunk);
                i += (CHUNK_SIZE - CHUNK_OVERLAP);
                if (i <= 0) break; // Avoid infinite loop if overlap > size
            }
            console.log(`Text split into ${chunks.length} chunks.`);
            return chunks;
        }

        /**
         * Simulates an embedding vector (to keep the demo runnable without a specific embedding endpoint).
         * In a real application, this would call the OpenAI/Gemini Embedding API.
         * The result vector is randomized but uses the correct dimension.
         */
        function generateSimulatedVector(text) {
            const vector = [];
            for (let i = 0; i < EMBEDDING_DIM; i++) {
                // Generate a random number between -1 and 1
                vector.push((Math.random() * 2) - 1);
            }
            return vector;
        }

        /**
         * Calculates Euclidean Distance (L2) between two vectors.
         * Smaller distance = higher similarity.
         */
        function euclideanDistance(vecA, vecB) {
            if (vecA.length !== vecB.length) {
                throw new Error("Vectors must have the same dimension for distance calculation.");
            }
            let sumOfSquares = 0;
            for (let i = 0; i < vecA.length; i++) {
                sumOfSquares += (vecA[i] - vecB[i]) ** 2;
            }
            return Math.sqrt(sumOfSquares);
        }

        /**
         * Retrieves the top K most similar chunks from the index.
         */
        function searchIndex(queryVector) {
            const results = indexStore.map(item => ({
                text: item.text,
                distance: euclideanDistance(queryVector, item.vector)
            }));

            // Sort by distance (ascending) and take the top K
            results.sort((a, b) => a.distance - b.distance);
            
            const topChunks = results.slice(0, TOP_K);
            
            return topChunks;
        }
        
        /**
         * Calls the Gemini API for the final RAG generation step.
         */
        async function generateRAGAnswer(query, context) {
            const systemPrompt = `You are an expert AI assistant tasked with answering user questions based *only* on the provided context.
If the context does not contain the answer, you must respond with: "I apologize, but the provided knowledge base does not contain enough information to answer this question."
Be concise, clear, and refer only to the facts presented in the context.`;
            
            const userQuery = `
Context:
---
${context}
---
Question: ${query}
`;

            try {
                const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${GENERATION_MODEL}:generateContent?key=${apiKey}`;
                
                const payload = {
                    contents: [{ parts: [{ text: userQuery }] }],
                    systemInstruction: { parts: [{ text: systemPrompt }] },
                };

                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    throw new Error(`API call failed with status: ${response.status}`);
                }

                const result = await response.json();
                const text = result.candidates?.[0]?.content?.parts?.[0]?.text;
                
                if (text) {
                    return text;
                } else {
                    return "Error: Could not extract text from API response.";
                }

            } catch (error) {
                console.error("Gemini API Error:", error);
                return `Error generating answer: ${error.message}`;
            }
        }


        // --- Main Workflow Handlers ---

        /**
         * Step 1: Chunks text and builds the in-memory index.
         */
        window.handleBuildIndex = function() {
            const rawText = kbTextarea.value.trim();
            if (rawText.length < 100) {
                statusMsg.textContent = "Please paste a substantial amount of text (at least 100 characters).";
                return;
            }

            buildBtn.disabled = true;
            statusMsg.textContent = "Indexing in progress: Chunking text...";
            indexStore = [];
            
            const chunks = chunkText(rawText);
            
            statusMsg.textContent = `Indexing in progress: Generating ${chunks.length} simulated embeddings...`;
            
            // Step 2: Simulate Embedding and store
            for (const chunk of chunks) {
                const vector = generateSimulatedVector(chunk);
                indexStore.push({ text: chunk, vector: vector });
            }

            buildBtn.classList.add('bg-green-600', 'hover:bg-green-700');
            buildBtn.classList.remove('bg-indigo-600', 'hover:bg-indigo-700');
            buildBtn.textContent = `Index Built! Total chunks: ${indexStore.length}`;
            statusMsg.textContent = `Success! Index is ready with ${indexStore.length} chunks. You can now ask questions.`;
            
            queryInput.disabled = false;
            queryBtn.disabled = false;
            kbTextarea.disabled = true; // Lock KB after indexing
            queryInput.focus();
        };

        /**
         * Step 2/3: Embeds query, retrieves context, and generates RAG answer.
         */
        window.handleQuery = async function() {
            const query = queryInput.value.trim();
            if (!query) return;
            if (indexStore.length === 0) {
                answerOutput.innerHTML = `<span class="text-red-600">ERROR: Please build the index first.</span>`;
                return;
            }

            queryBtn.disabled = true;
            loadingIndicator.classList.remove('hidden');
            answerOutput.textContent = '';
            contextOutput.textContent = 'Searching index...';
            
            try {
                // Step 2.1: Simulate Query Embedding
                // In a real RAG, this would be an API call, but we simulate it for stability.
                const queryVector = generateSimulatedVector(query);

                // Step 2.2: Retrieve Top K Chunks
                const topChunks = searchIndex(queryVector);
                const context = topChunks.map((c, i) => 
                    `[Chunk ${i + 1}, Distance: ${c.distance.toFixed(4)}]\n${c.text}`
                ).join('\n\n---\n\n');
                
                contextOutput.textContent = context;
                loadingIndicator.classList.remove('hidden');

                // Step 2.3: Generate Grounded Answer (Real API Call)
                answerOutput.textContent = 'Generating answer with Gemini...';
                const finalAnswer = await generateRAGAnswer(query, context);
                answerOutput.textContent = finalAnswer;

            } catch (error) {
                answerOutput.innerHTML = `<span class="text-red-600">An error occurred during query or generation: ${error.message}</span>`;
            } finally {
                queryBtn.disabled = false;
                loadingIndicator.classList.add('hidden');
            }
        };

        // Initialize UI State
        window.onload = () => {
             buildBtn.disabled = kbTextarea.value.length < 100;
        };
    </script>
</body>
</html>
