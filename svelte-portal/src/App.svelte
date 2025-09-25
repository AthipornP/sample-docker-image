
<script>
	import { onMount } from 'svelte';
	import Navbar from './Navbar.svelte';
	export let name;

	let currentTime = new Date().toLocaleString();
	let user = null;
	let loading = true;

	// Local SVG asset paths (served from public/)
	const svgDjango = '/assets/django.svg';
	const svgDotnet = '/assets/dotnet.svg';
	const svgPhp = '/assets/php.svg';

	// helper to produce highlighted JSON where keys and values have different colors
	function syntaxHighlight(json) {
		if (typeof json !== 'string') json = JSON.stringify(json, null, 2);
		json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
		return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?)|(\b(true|false|null)\b)|(-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
			let cls = 'number';
			if (/^\"/.test(match)) {
				if (/:$/.test(match)) {
					cls = 'key';
				} else {
					cls = 'string';
				}
			} else if (/true|false/.test(match)) {
				cls = 'boolean';
			} else if (/null/.test(match)) {
				cls = 'null';
			}
			return '<span class="' + cls + '">' + match + '</span>';
		});
	}

	async function fetchUser() {
		try {
			const res = await fetch('/api/user');
			const data = await res.json();
			if (data.authenticated) {
				user = data.claims;
			} else {
				user = null;
			}
		} finally {
			loading = false;
		}
	}


	// no runtime fetching required — assets live under public/assets

	fetchUser();

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
</script>

<main>
	<Navbar />
	<div class="hero-section">
		<div class="hero-content">
			<h1>Welcome to Customer Portal</h1>
			<p class="hero-subtitle">Your gateway to excellent customer service</p>
			{#if loading}
				<p>Loading authentication...</p>
			{:else}
				{#if user}
					<button on:click={logout} style="margin-top:1rem">Logout</button>
					<div class="claims-box">
						<h2>User Claims</h2>
						<pre>{@html syntaxHighlight(user)}</pre>
					</div>
				{:else}
					<button on:click={login} style="margin-top:1rem">Login with SSO</button>
				{/if}
			{/if}
		</div>
	</div>

	<div class="container">
		<div class="dashboard-grid">
			<div class="card">
				<div class="card-icon"><img src="{svgDjango}" alt="Django logo" /></div>
				<h3>Django App</h3>
				<p>Open the Django application</p>
				<a class="link-button" href="http://localhost:8000" target="_blank" rel="noopener noreferrer">Open Django</a>
			</div>

			<div class="card">
				<div class="card-icon"><img src="{svgDotnet}" alt="Dotnet logo" /></div>
				<h3>.NET 8</h3>
				<p>Open the .NET 8 application</p>
				<a class="link-button" href="http://localhost:5000" target="_blank" rel="noopener noreferrer">Open .NET App</a>
			</div>

			<div class="card">
				<div class="card-icon"><img src="{svgPhp}" alt="PHP logo" /></div>
				<h3>PHP</h3>
				<p>Open the PHP application</p>
				<a class="link-button" href="http://localhost:8080" target="_blank" rel="noopener noreferrer">Open PHP</a>
			</div>
		</div>
		
		<div class="status-bar">
			<div class="status-item">
				<span class="status-label">Portal Status:</span>
				<span class="status-value online">Online</span>
			</div>
			<div class="status-item">
				<span class="status-label">Current Time:</span>
				<span class="status-value">{currentTime}</span>
			</div>
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
		text-align: center;
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
	}
	
	.hero-content h1 {
		font-size: 3.5rem;
		margin-bottom: 1rem;
		font-weight: 700;
		text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
	}
	
	.hero-subtitle {
		font-size: 1.5rem;
		opacity: 0.9;
		margin-bottom: 0;
	}
	
	.container {
		max-width: 1200px;
		margin: 0 auto;
		padding: 3rem 1rem;
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
		text-align: center;
	}
	
	.card p {
		color: #424242;
		/* allow content to grow and push button to bottom */
		margin: 0 0 1rem 0;
		line-height: 1.6;
		text-align: center;
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
		background: #e3f2fd;
		color: #0d47a1;
		border-radius: 8px;
		margin: 2rem auto 0 auto;
		padding: 1.5rem 2rem;
		max-width: 600px;
		box-shadow: 0 2px 8px rgba(33, 150, 243, 0.08);
		text-align: left;
	}
	.claims-box pre {
		background: #fff;
		color: #222;
		border-radius: 4px;
		padding: 1rem;
		font-size: 1rem;
		overflow-x: auto;
	}


	/* Key / value colorization for JSON (use global selectors because content is inserted via {@html}) */
	:global(.key) { color: #e65100; font-weight: 700; }
	/* values use blue to match portal theme */
	:global(.string), :global(.number), :global(.boolean), :global(.null) { color: #0d47a1; }
</style>