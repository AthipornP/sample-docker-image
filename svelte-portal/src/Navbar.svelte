<nav>
	<div class="navbar">
		<div class="navbar-brand">
			<a href="/">🏢 Customer Portal</a>
		</div>
		<div class="navbar-menu">
			<a href="/" class="navbar-item">🏠 Dashboard</a>
			<a href="/account" class="navbar-item">👤 My Account</a>
			<a href="/support" class="navbar-item">🎧 Support</a>
			<a href="/profile" class="navbar-item">⚙️ Settings</a>
		</div>
	</div>
</nav>

<style>
	.navbar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem 2rem;
		background: linear-gradient(90deg, #0d47a1 0%, #1976d2 50%, #42a5f5 100%);
		color: white;
		box-shadow: 0 4px 12px rgba(13, 71, 161, 0.3);
	}
	
	.navbar-brand a {
		font-size: 1.5rem;
		font-weight: bold;
		color: white;
		text-decoration: none;
	}
	
	.navbar-menu {
		display: flex;
		gap: 1.5rem;
	}
	
	.navbar-item {
		color: white;
		text-decoration: none;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		transition: background-color 0.2s;
	}
	
	.navbar-item:hover {
		background-color: rgba(255, 255, 255, 0.2);
		transform: translateY(-1px);
	}
</style>