async function showGames(folderId) {
  // Clear search mode when showing folder games
  isSearchMode = false;
  document.getElementById('searchInput').value = '';
  document.getElementById('clearSearch').style.display = 'none';
  document.getElementById('folderContainer').style.display = 'flex';
  
  const container = document.getElementById('gamesContainer');
  container.innerHTML = '<p style="text-align: center; color: var(--muted);">Loading games...</p>';
  
  try {
    const response = await fetch(`/api/public/folders/${folderId}/games/`);
    const games = await response.json();
    
    container.innerHTML = '';
    
    if (games.length === 0) {
      container.innerHTML = `<p style="grid-column: 1/-1; text-align:center; color: var(--muted);">No games available in this folder yet.</p>`;
      return;
    }
    
    games.forEach(game => {
      const card = document.createElement('div');
      card.className = 'game-card';
      card.innerHTML = `
        <h3>${game.name}</h3>
        <p><strong>Players:</strong> ${game.number_of_players}</p>
        <p><strong>Time:</strong> ${game.time}</p>
        ${game.materials ? `<p><strong>Materials:</strong> ${game.materials}</p>` : ''}
        <p>${game.description || ''}</p>
        <a href="/game/${game.id}/" class="btn btn-primary">View Details</a>
      `;
      container.appendChild(card);
    });
  } catch (error) {
    console.error('Error loading games:', error);
    container.innerHTML = `<p style="grid-column: 1/-1; text-align:center; color: #e74c3c;">Error loading games. Please try again.</p>`;
  }
}

// Search functionality
let searchTimeout;
let isSearchMode = false;

async function searchGames(query) {
  if (!query.trim()) {
    clearSearch();
    return;
  }

  try {
    isSearchMode = true;
    const response = await fetch(`/api/public/search/?q=${encodeURIComponent(query)}`);
    const data = await response.json();
    
    const container = document.getElementById('gamesContainer');
    const folderContainer = document.getElementById('folderContainer');
    
    // Hide folders when searching
    folderContainer.style.display = 'none';
    container.innerHTML = '';

    if (data.results.length === 0) {
      container.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; color: var(--muted); padding: 40px;">
          <h3>No games found</h3>
          <p>No games match your search for "${query}"</p>
        </div>
      `;
      return;
    }

    // Show search results header
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; margin-bottom: 20px; color: var(--accent);">
        <h3>Search Results (${data.count} found)</h3>
        <p>Searching for: "${query}"</p>
      </div>
    `;

    data.results.forEach(game => {
      const card = document.createElement('div');
      card.className = 'game-card';
      card.innerHTML = `
        <h3>${game.name}</h3>
        <p><strong>Players:</strong> ${game.number_of_players}</p>
        <p><strong>Time:</strong> ${game.time}</p>
        <p><strong>Categories:</strong> ${game.folder_names.join(', ') || 'None'}</p>
        ${game.materials ? `<p><strong>Materials:</strong> ${game.materials}</p>` : ''}
        <p>${game.description || ''}</p>
        <a href="/game/${game.id}/" class="btn btn-primary">View Details</a>
      `;
      container.appendChild(card);
    });

  } catch (error) {
    console.error('Search error:', error);
    const container = document.getElementById('gamesContainer');
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; color: #e74c3c; padding: 40px;">
        <h3>Search Error</h3>
        <p>Failed to search games. Please try again.</p>
      </div>
    `;
  }
}

function clearSearch() {
  isSearchMode = false;
  document.getElementById('searchInput').value = '';
  document.getElementById('clearSearch').style.display = 'none';
  document.getElementById('gamesContainer').innerHTML = '';
  document.getElementById('folderContainer').style.display = 'flex';
}

function handleSearchInput() {
  const query = document.getElementById('searchInput').value.trim();
  const clearBtn = document.getElementById('clearSearch');
  
  if (query) {
    clearBtn.style.display = 'block';
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => searchGames(query), 300); // Debounce search
  } else {
    clearBtn.style.display = 'none';
    clearSearch();
  }
}

// Initialize search functionality when page loads
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('searchInput');
  const clearSearchBtn = document.getElementById('clearSearch');
  
  if (searchInput) {
    searchInput.addEventListener('input', handleSearchInput);
    searchInput.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        clearSearch();
      }
    });
  }
  
  if (clearSearchBtn) {
    clearSearchBtn.addEventListener('click', clearSearch);
  }
});
