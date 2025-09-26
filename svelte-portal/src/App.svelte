<script>
	import { onMount } from 'svelte';
	import Navbar from './Navbar.svelte';
	import MarkdownViewer from './MarkdownViewer.svelte';
	export let name;

	let currentTime = new Date().toLocaleString();
	let user = null;
	let userMarkdown = '';
	let loading = true;
	let accessToken = null;

	let apps = [];

	// API test fields
 	let apiEndpoint = '';
 	let apiResponse = null;
	let responseMarkdown = '';
 	let apiLoading = false;
	let apiError = null;
	let codeSnippet = '';
	let showCode = false;
	let selectedLang = 'javascript';
	let codeByLang = {};



	// Local SVG asset paths (served from public/)
	const svgDjango = '/assets/django.svg';
	const svgDotnet = '/assets/dotnet.svg';
	const svgPhp = '/assets/php.svg';

	// helper to produce highlighted JSON where keys and values have different colors


	async function fetchUser() {
		try {
			const res = await fetch('/api/user');
			const data = await res.json();
			if (data.authenticated) {
				user = data.claims;
				userMarkdown = '```json\n' + JSON.stringify(data.claims, null, 2) + '\n```';
				accessToken = data.access_token || null;
			} else {
				user = null;
				userMarkdown = '';
			}
		} finally {
			loading = false;
		}
	}

	async function fetchApps() {
		try {
			const res = await fetch('/api/apps');
			if (res.ok) {
				const json = await res.json();
				apps = json.apps || [];
				// if server returned api urls (from .env), prefer them
				if (json.api && json.api.django) {
					// use API_DJANGO_URL if available
					apiEndpoint = json.api.django;
				}
				// if no apiEndpoint provided by user yet, prefill from env-configured apps
				if (!apiEndpoint) {
					apiEndpoint = buildDefaultEndpoint();
				}
			}
		} catch (e) {
			console.warn('Failed to fetch apps', e && e.message ? e.message : e);
		}
	}


	// no runtime fetching required — assets live under public/assets

	fetchUser();
	fetchApps();

	// Update time every second
	setInterval(() => {
		currentTime = new Date().toLocaleString();
	}, 1000);

	function login() {
		window.location.href = '/auth/login';
	}
	function logout() {
		window.location.href = '/auth/logout';
	}

	function openApp(url) {
		// navigate in the same tab to the app
		window.location.href = url;
	}


	function buildDefaultEndpoint() {
		// try to guess a django app url from apps array
		const django = apps.find(a => a.id === 'django' || a.id === 'django-api');
		if (django && django.url) return django.url.replace(/\/$/, '') + '/api/test';
		return '/api/test';
	}

	async function callApi() {
		apiError = null;
		apiResponse = null;
		responseMarkdown = '';
		apiLoading = true;
		try {
			const url = apiEndpoint || buildDefaultEndpoint();
			// build the code snippet for display
			codeSnippet = `// Example: call Django API with access token\nfetch('${url}', {\n  method: 'GET',\n  headers: {\n    'Authorization': 'Bearer ${accessToken}',\n    'Accept': 'application/json'\n  }\n})\n  .then(r => r.json())\n  .then(json => console.log(json))\n  .catch(err => console.error(err));`;

			// render as markdown code block for nicer display
			// build snippets for multiple languages in markdown format
			codeByLang = {
				javascript: `\`\`\`javascript\n// JavaScript (fetch)\n${codeSnippet}\n\`\`\``,
				python: `\`\`\`python\n# Python (requests)\nimport requests\nheaders = {'Authorization': 'Bearer ${accessToken}', 'Accept': 'application/json'}\nresp = requests.get('${url}', headers=headers)\nprint(resp.status_code)\nprint(resp.text)\n\`\`\``,
				csharp: `\`\`\`cs\n// C# (.NET HttpClient)\nusing var client = new System.Net.Http.HttpClient();\nclient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", "${accessToken}");\nvar res = await client.GetAsync("${url}");\nvar text = await res.Content.ReadAsStringAsync();\nConsole.WriteLine(text);\n\`\`\``,
				php: `\`\`\`php\n// PHP (cURL)\n$ch = curl_init();\ncurl_setopt($ch, CURLOPT_URL, '${url}');\ncurl_setopt($ch, CURLOPT_RETURNTRANSFER, true);\ncurl_setopt($ch, CURLOPT_HTTPHEADER, ['Authorization: Bearer ${accessToken}', 'Accept: application/json']);\n$response = curl_exec($ch);\ncurl_close($ch);\necho $response;\n\`\`\``,
				curl: `\`\`\`bash\n# curl\ncurl -H "Authorization: Bearer ${accessToken}" -H "Accept: application/json" "${url}"\n\`\`\``
			};



			const res = await fetch(url, {
				headers: {
					'Authorization': accessToken ? `Bearer ${accessToken}` : '',
					'Accept': 'application/json'
				}
			});
			const text = await res.text();
			try {
				apiResponse = JSON.parse(text);
				// สร้าง markdown สำหรับ JSON response
				responseMarkdown = '```json\n' + JSON.stringify(apiResponse, null, 2) + '\n```';
			} catch (e) {
				// not JSON
				apiResponse = text;
				// สร้าง markdown สำหรับ plain text response
				responseMarkdown = '```\n' + text + '\n```';
			}
			if (!res.ok) {
				apiError = `HTTP ${res.status}: ${res.statusText}`;
			}
		} catch (e) {
			apiError = e && e.message ? e.message : String(e);
		} finally {
			apiLoading = false;
		}
	}

	function selectLang(lang) {
		selectedLang = lang;
	}
</script>

<main>
	<Navbar />
	<div class="hero-section">
		<div class="hero-content">
			<h1>Welcome to Customer Portal</h1>
			<p class="hero-subtitle">All apps authenticate with Keycloak SSO</p>
			{#if loading}
				<p>Loading authentication...</p>
			{:else}
				{#if user}
					<button class="auth-button" on:click={logout}>Logout</button>
					<div class="claims-box">
						<h2 style="color: #e2e8f0;">User Claims</h2>
						<MarkdownViewer source={userMarkdown} />
					</div>
					<div>
						{#if accessToken}
							<h3>Access token</h3>
							<pre class="token-block"><code>{accessToken}</code></pre>
						{/if}
					</div>

					<!-- API Test Section -->
					{#if accessToken}
						<div class="api-test">
							<div class="api-header">
								<h2>🔧 API Test</h2>
								<p class="api-subtitle">Test Django API with your access token</p>
							</div>
							
							<div class="api-endpoint-section">
								<div class="endpoint-label">API Endpoint:</div>
								<div class="endpoint-display">
									<span class="endpoint-url">{apiEndpoint}</span>
									<div class="endpoint-badge">GET</div>
								</div>
							</div>

							<div class="api-controls">
								<button class="call-api-button" on:click={callApi} disabled={apiLoading}>
									{#if apiLoading}
										<span class="loading-spinner"></span>
										Calling...
									{:else}
										<span class="call-icon">🚀</span>
										Call API
									{/if}
								</button>
								<button class="show-code-button" on:click={() => showCode = !showCode}>
									<span class="code-icon">{showCode ? '🙈' : '💻'}</span>
									{showCode ? 'Hide Code' : 'Show Code'}
								</button>
							</div>

							{#if apiError}
								<div class="api-error">
									<div class="error-icon">❌</div>
									<div class="error-content">
										<strong>Error:</strong>
										<span>{apiError}</span>
									</div>
								</div>
							{/if}

							{#if apiResponse}
								<div class="api-response">
									<div class="response-header">
										<h3>📋 Response</h3>
										<div class="success-badge">200 OK</div>
									</div>
									<div class="response-content">
										<MarkdownViewer source={responseMarkdown} />
									</div>
								</div>
							{/if}

							{#if showCode}
								<div class="api-code">
									<div class="code-header">
										<h3>👨‍💻 Code Examples</h3>
										<p class="code-subtitle">Copy and use in your application</p>
									</div>
									
									<div class="lang-buttons">
										{#each Object.keys(codeByLang) as lang}
											<button 
												class="lang-button" 
												class:active={selectedLang===lang} 
												on:click={() => selectLang(lang)}
											>
												<span class="lang-icon">
													{#if lang === 'javascript'}🟨
													{:else if lang === 'python'}🐍
													{:else if lang === 'csharp'}🔷
													{:else if lang === 'php'}🐘
													{:else if lang === 'curl'}⚡
													{:else}📝{/if}
												</span>
												{lang === 'csharp' ? 'C#' : lang.charAt(0).toUpperCase() + lang.slice(1)}
											</button>
										{/each}
									</div>
									
									<div class="code-block-container">
										<MarkdownViewer source={codeByLang[selectedLang]} />
									</div>
								</div>
							{/if}
						</div>
					{/if}
				{:else}
						<button class="auth-button" on:click={login}>Login with SSO</button>
					{/if}
			{/if}
		</div>
	</div>

	<div class="container">
		<div class="dashboard-grid">
			{#if apps.length === 0}
				<div>Loading services...</div>
			{:else}
				{#each apps as app}
					<div class="card" key={app.id}>
						<div class="card-icon">
							<img src={app.id === 'django' ? svgDjango : app.id === 'dotnet' ? svgDotnet : svgPhp} alt={app.name} />
						</div>
						<h3>{app.name}</h3>
						<p>Open the {app.name} — listening at <strong class="status-value">{app.url}</strong></p>
						<button class="link-button" on:click={() => openApp(app.url)}>Open {app.name}</button>
					</div>
					{/each}
			{/if}
		</div>
	</div>
</main>

<style>
	main {
		padding: 0;
		margin: 0;
		min-height: 100vh;
	}
	
	.hero-section {
		background: linear-gradient(135deg, #0d47a1 0%, #1976d2 50%, #42a5f5 100%);
		color: white;
		padding: 4rem 2rem;
		text-align: left; /* เปลี่ยนจาก center เป็น left */
		position: relative;
		overflow: hidden;
	}
	
	.hero-section::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="25" cy="25" r="2" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1.5" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="1" fill="white" opacity="0.1"/></svg>');
		animation: float 20s infinite linear;
	}
	
	@keyframes float {
		from { transform: translateY(0px); }
		to { transform: translateY(-100px); }
	}
	
	.hero-content {
		position: relative;
		z-index: 1;
		text-align: center; /* restored to center */
	}
	
	.hero-content h1 {
		font-size: 3.5rem;
		margin-bottom: 1rem;
		font-weight: 700;
		text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
		text-align: center; /* restored to center */
	}
	
	.hero-subtitle {
		font-size: 1.5rem;
		opacity: 0.9;
		margin-bottom: 0;
		text-align: center; /* restored to center */
	}
	
	.container {
		max-width: 1200px;
		margin: 0 auto; /* center container horizontally */
		padding: 3rem 1rem;
		text-align: center; /* restored to center */
	}
	
	.dashboard-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: 2rem;
		margin-bottom: 3rem;
	}
	
	.card {
		background: white;
		border-radius: 12px;
		padding: 2rem;
		box-shadow: 0 8px 32px rgba(13, 71, 161, 0.1);
		transition: all 0.3s ease;
		border: 2px solid #e3f2fd;
		overflow: hidden; /* keep buttons and icons inside rounded card */
		display: flex;
		flex-direction: column;
		align-items: center;
	}
	
	.card:hover {
		transform: translateY(-4px);
		box-shadow: 0 16px 48px rgba(13, 71, 161, 0.2);
		border-color: #bbdefb;
	}
	
	.card-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 64px;
		margin-bottom: 1rem;
		text-align: center;
		/* ensure SVGs fit nicely */
	}

	.card-icon img, .card-icon svg {
		width: 48px;
		height: 48px;
		object-fit: contain;
	}
	
	.card h3 {
		color: #0d47a1;
		margin-bottom: 1rem;
		font-size: 1.5rem;
		text-align: center; /* restored to center */
	}
	
	.card p {
		color: #424242;
		/* allow content to grow and push button to bottom */
		margin: 0 0 1rem 0;
		line-height: 1.6;
		text-align: center; /* restored to center */
	}
	
	.card button {
		width: 100%;
		padding: 0.75rem 1.5rem;
		background: linear-gradient(90deg, #1976d2, #42a5f5);
		border: none;
		color: white;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
	}
	
	.card button:hover {
		background: linear-gradient(90deg, #1565c0, #2196f3);
		transform: translateY(-1px);
	}

	/* prominent orange auth buttons for Login / Logout */
	.auth-button {
		display: inline-block;
		margin-top: 1rem;
		padding: 0.75rem 1.5rem;
		background: linear-gradient(90deg, #ff8a00, #ff5722);
		border: none;
		color: white;
		border-radius: 10px;
		font-weight: 700;
		cursor: pointer;
		box-shadow: 0 8px 24px rgba(255, 138, 0, 0.18);
		transition: transform 0.12s ease, box-shadow 0.12s ease, filter 0.12s ease;
	}

	.auth-button:hover {
		transform: translateY(-2px);
		filter: brightness(1.02);
		box-shadow: 0 12px 36px rgba(255, 87, 34, 0.22);
	}

	.auth-button:focus {
		outline: 3px solid rgba(255, 138, 0, 0.18);
		outline-offset: 2px;
	}

	/* make anchor links look like buttons inside cards and remain contained */
	.card .link-button {
		display: block;
		box-sizing: border-box;
		width: 100%;
		text-align: center;
		padding: 0.75rem 1.5rem;
		background: linear-gradient(90deg, #1976d2, #42a5f5);
		color: white;
		border-radius: 8px;
		font-weight: 600;
		text-decoration: none;
	}

	.card .link-button:hover {
		background: linear-gradient(90deg, #1565c0, #2196f3);
		transform: translateY(-1px);
	}

	/* push link-button to the bottom of the card */
	.card .link-button {
		margin-top: auto;
		align-self: stretch;
	}
	
	.status-bar {
		background: white;
		border-radius: 12px;
		padding: 1.5rem 2rem;
		box-shadow: 0 4px 16px rgba(13, 71, 161, 0.1);
		border: 2px solid #e3f2fd;
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex-wrap: wrap;
		gap: 1rem;
	}
	
	.status-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	
	.status-label {
		color: #666;
		font-weight: 500;
	}
	
	.status-value {
		color: #0d47a1;
		font-weight: 600;
	}
	
	.status-value.online {
		color: #4caf50;
		display: flex;
		align-items: center;
	}
	
	.status-value.online::before {
		content: '\25CF';
		margin-right: 0.25rem;
		animation: pulse 2s infinite;
	}
	
	@keyframes pulse {
		0% { opacity: 1; }
		50% { opacity: 0.5; }
		100% { opacity: 1; }
	}
	
	@media (max-width: 768px) {
		.hero-content h1 {
			font-size: 2.5rem;
		}
		
		.hero-subtitle {
			font-size: 1.2rem;
		}
		
		.dashboard-grid {
			grid-template-columns: 1fr;
		}
		
		.status-bar {
			flex-direction: column;
			align-items: flex-start;
		}
	}

	.claims-box {
		background: #282c34;
		color: #e2e8f0;
		border-radius: 8px;
		margin: 2rem auto 0 auto;
		padding: 1.5rem 2rem;
		max-width: 600px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
		text-align: left;
	}


	/* API test area */
	.api-test {
		background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
		border-radius: 16px;
		padding: 2rem;
		margin: 2rem auto 0 auto;
		max-width: 900px;
		text-align: left;
		box-shadow: 0 8px 32px rgba(13, 71, 161, 0.12);
		border: 2px solid #e3f2fd;
		position: relative;
		overflow: hidden;
	}

	.api-test::before {
		content: '';
		position: absolute;
		top: 0;
		right: 0;
		width: 100px;
		height: 100px;
		background: linear-gradient(135deg, #42a5f5 0%, #1976d2 100%);
		opacity: 0.05;
		border-radius: 50%;
		transform: translate(30px, -30px);
	}

	.api-header {
		margin-bottom: 1.5rem;
		position: relative;
		z-index: 1;
	}

	.api-header h2 {
		color: #0d47a1;
		margin: 0 0 0.5rem 0;
		font-size: 1.8rem;
		font-weight: 700;
	}

	.api-subtitle {
		color: #666;
		margin: 0;
		font-size: 1rem;
		opacity: 0.8;
	}

	.api-endpoint-section {
		background: #f8faff;
		border: 2px solid #e3f2fd;
		border-radius: 12px;
		padding: 1rem;
		margin-bottom: 1.5rem;
	}

	.endpoint-label {
		display: block;
		color: #0d47a1;
		font-weight: 600;
		font-size: 0.9rem;
		margin-bottom: 0.5rem;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.endpoint-display {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.endpoint-url {
		flex: 1;
		background: #fff;
		padding: 0.75rem 1rem;
		border-radius: 8px;
		border: 1px solid #cfe3ff;
		color: #1565c0;
		font-family: 'Consolas', 'Monaco', monospace;
		font-size: 0.9rem;
	}

	.endpoint-badge {
		background: linear-gradient(90deg, #4caf50, #66bb6a);
		color: white;
		padding: 0.5rem 0.75rem;
		border-radius: 6px;
		font-weight: 600;
		font-size: 0.8rem;
		letter-spacing: 0.5px;
	}

	.api-controls {
		display: flex;
		gap: 1rem;
		margin-bottom: 1.5rem;
	}

	.call-api-button {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 0.875rem 1.5rem;
		background: linear-gradient(90deg, #ff8a00, #ff5722);
		border: none;
		color: white;
		border-radius: 12px;
		font-weight: 700;
		cursor: pointer;
		transition: all 0.3s ease;
		box-shadow: 0 4px 16px rgba(255, 87, 34, 0.3);
		font-size: 1rem;
	}

	.call-api-button:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 8px 24px rgba(255, 87, 34, 0.4);
	}

	.call-api-button:disabled {
		opacity: 0.7;
		cursor: not-allowed;
	}

	.show-code-button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.875rem 1.5rem;
		background: linear-gradient(90deg, #6a1b9a, #8e24aa);
		border: none;
		color: white;
		border-radius: 12px;
		font-weight: 700;
		cursor: pointer;
		transition: all 0.3s ease;
		box-shadow: 0 4px 16px rgba(106, 27, 154, 0.3);
		font-size: 1rem;
	}

	.show-code-button:hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 24px rgba(106, 27, 154, 0.4);
	}

	.loading-spinner {
		width: 16px;
		height: 16px;
		border: 2px solid rgba(255, 255, 255, 0.3);
		border-top: 2px solid white;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	.api-error {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		background: linear-gradient(90deg, #ffebee, #fff0f1);
		border: 2px solid #ffcdd2;
		border-radius: 12px;
		padding: 1rem;
		margin-bottom: 1.5rem;
	}

	.error-icon {
		font-size: 1.2rem;
		flex-shrink: 0;
	}

	.error-content {
		flex: 1;
		color: #b00020;
	}

	.error-content strong {
		display: block;
		margin-bottom: 0.25rem;
	}

	.api-response {
		background: #282c34;
		border: 2px solid #4a5568;
		border-radius: 12px;
		margin-bottom: 1.5rem;
		overflow: hidden;
	}

	.response-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem;
		background: linear-gradient(90deg, #1a202c, #2d3748);
		border-bottom: 1px solid #4a5568;
	}

	.response-header h3 {
		margin: 0;
		color: #e2e8f0;
		font-size: 1.1rem;
	}

	.success-badge {
		background: linear-gradient(90deg, #4caf50, #66bb6a);
		color: white;
		padding: 0.25rem 0.5rem;
		border-radius: 6px;
		font-size: 0.8rem;
		font-weight: 600;
	}

	.response-content {
		padding: 1rem;
		background: #282c34;
		color: #e2e8f0;
	}



	.api-code {
		background: #fafbff;
		border: 2px solid #e0e7ff;
		border-radius: 12px;
		overflow: hidden;
	}

	.code-header {
		padding: 1rem;
		background: linear-gradient(90deg, #f1f5f9, #fafbff);
		border-bottom: 1px solid #e0e7ff;
	}

	.code-header h3 {
		margin: 0 0 0.5rem 0;
		color: #334155;
		font-size: 1.1rem;
	}

	.code-subtitle {
		margin: 0;
		color: #64748b;
		font-size: 0.9rem;
	}

	.lang-buttons {
		display: flex;
		gap: 0.5rem;
		padding: 1rem;
		background: #f8fafc;
		border-bottom: 1px solid #e0e7ff;
		flex-wrap: wrap;
	}

	.lang-button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.75rem;
		border-radius: 8px;
		border: 2px solid #e2e8f0;
		background: #fff;
		cursor: pointer;
		transition: all 0.2s ease;
		font-weight: 600;
		font-size: 0.9rem;
		color: #475569;
	}

	.lang-button:hover {
		border-color: #94a3b8;
		transform: translateY(-1px);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.lang-button.active {
		background: linear-gradient(90deg, #3b82f6, #60a5fa);
		color: white;
		border-color: #2563eb;
		box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
	}

	.lang-icon {
		font-size: 1rem;
	}

	.code-block-container {
		padding: 1rem;
		background: #fff;
	}

	/* Custom dark theme that works with local Prism.js */
	.code-block-container {
		background: #2d3748;
		border-radius: 8px;
		border: 1px solid #4a5568;
		overflow: hidden;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}

	/* Force override Prism's default styles with highest priority */
	/* ให้ highlight.js จัดการสีเอง - ไม่ override */
	.code-block-container :global(pre) {
		padding: 1.5rem;
		margin: 0;
		border-radius: 0;
		border: none;
		font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
		font-size: 0.9rem;
		line-height: 1.6;
		overflow-x: auto;
		white-space: pre;
		text-shadow: none;
	}

	.code-block-container :global(code) {
		font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
		font-size: 0.9rem;
		line-height: 1.6;
		text-shadow: none;
		white-space: pre;
	}


	.token-block {
		background:#071226;
		color:#dbeefd;
		padding:12px;
		border-radius:8px;
		overflow:auto;
		white-space:pre-wrap; /* allow wrapping */
		word-break:break-word;
		/* ensure only the token block content is left-aligned */
		text-align: left;
	}


	/* Key / value colorization for JSON (use global selectors because content is inserted via {@html}) */
	:global(.key) { color: #e65100; font-weight: 700; }
	/* values use blue to match portal theme */
	:global(.string), :global(.number), :global(.boolean), :global(.null) { color: #0d47a1; }
</style>