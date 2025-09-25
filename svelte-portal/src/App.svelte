<script>
	import Navbar from './Navbar.svelte';
	export let name;
	
	let currentTime = new Date().toLocaleString();
	
	// Update time every second
	setInterval(() => {
		currentTime = new Date().toLocaleString();
	}, 1000);
</script>

<main>
	<Navbar />
	<div class="hero-section">
		<div class="hero-content">
			<h1>Welcome to Customer Portal</h1>
			<p class="hero-subtitle">Your gateway to excellent customer service</p>
		</div>
	</div>
	
	<div class="container">
		<div class="dashboard-grid">
			<div class="card">
				<div class="card-icon">📊</div>
				<h3>Account Overview</h3>
				<p>View your account details and current status</p>
				<button>View Details</button>
			</div>
			
			<div class="card">
				<div class="card-icon">📋</div>
				<h3>Service Requests</h3>
				<p>Submit and track your service requests</p>
				<button>Manage Requests</button>
			</div>
			
			<div class="card">
				<div class="card-icon">💳</div>
				<h3>Billing & Payments</h3>
				<p>View invoices and manage payment methods</p>
				<button>View Billing</button>
			</div>
			
			<div class="card">
				<div class="card-icon">📞</div>
				<h3>Support Center</h3>
				<p>Get help and contact customer support</p>
				<button>Get Support</button>
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
	}
	
	.card:hover {
		transform: translateY(-4px);
		box-shadow: 0 16px 48px rgba(13, 71, 161, 0.2);
		border-color: #bbdefb;
	}
	
	.card-icon {
		font-size: 3rem;
		margin-bottom: 1rem;
		text-align: center;
	}
	
	.card h3 {
		color: #0d47a1;
		margin-bottom: 1rem;
		font-size: 1.5rem;
		text-align: center;
	}
	
	.card p {
		color: #424242;
		margin-bottom: 1.5rem;
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
		content: '●';
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
</style>