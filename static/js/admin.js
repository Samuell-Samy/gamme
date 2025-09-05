let currentFolder = null; // set from admin.html inline script

// Show games inside a folder
// showGames is now defined inline in admin.html to hit the API

// Game detail modal
function openModal(title, desc, link) {
  document.getElementById('modalTitle').textContent = title;
  document.getElementById('modalDesc').textContent = desc;
  const linkEl = document.getElementById('modalLink');
  if (link && link !== '#') {
    linkEl.href = link;
    linkEl.style.display = 'inline-block';
  } else {
    linkEl.href = '#';
    linkEl.style.display = 'none';
  }
  document.getElementById('gameModal').style.display = 'flex';
}

function closeModal() {
  document.getElementById('gameModal').style.display = 'none';
}

// ---------------- GAME FORM MODAL ---------------- //
function openGameFormModal(initial = { name: "", number_of_players: "", time: "", materials: "", description: "", video_link: "", folder_ids: [] }, onSave) {
  document.getElementById('gameFormTitle').textContent = initial.name ? 'Edit Game' : 'Add Game';
  document.getElementById('gameName').value = initial.name || '';
  document.getElementById('gamePlayers').value = initial.number_of_players || '';
  document.getElementById('gameTime').value = initial.time || '';
  document.getElementById('gameMaterials').value = initial.materials || '';
  document.getElementById('gameDesc').value = initial.description || '';
  document.getElementById('gameLink').value = initial.video_link || '';

  // populate folders multiselect from DOM folders list
  const select = document.getElementById('gameFoldersSelect');
  select.innerHTML = '';
  // Pull existing folders from DOM container
  const folderContainer = document.getElementById('folderContainer');
  const items = folderContainer.querySelectorAll('.folder');
  items.forEach((el, idx) => {
    const option = document.createElement('option');
    option.text = el.textContent;
    // We don't have id attached on element, so fetch again via API to get mapping when needed
    // For now, we rely on loadFolders attaching data-id attributes
  });

  // Better: fetch folders list fresh and mark selected
  fetchJSON('/api/folders/').then(folders => {
    select.innerHTML = '';
    folders.forEach(f => {
      const option = document.createElement('option');
      option.value = String(f.id);
      option.textContent = f.name;
      if (initial.folder_ids && initial.folder_ids.includes(f.id)) {
        option.selected = true;
      }
      select.appendChild(option);
    });
  }).catch(console.error);

  const modal = document.getElementById('gameFormModal');
  modal.style.display = 'flex';

  const form = document.getElementById('gameForm');
  const submitHandler = function(e) {
    e.preventDefault();
    const folderSelect = document.getElementById('gameFoldersSelect');
    const selectedFolderIds = Array.from(folderSelect.selectedOptions).map(o => parseInt(o.value));
    const payload = {
      name: document.getElementById('gameName').value.trim(),
      number_of_players: document.getElementById('gamePlayers').value.trim(),
      time: document.getElementById('gameTime').value.trim(),
      materials: document.getElementById('gameMaterials').value.trim(),
      description: document.getElementById('gameDesc').value.trim(),
      video_link: document.getElementById('gameLink').value.trim(),
      folder_ids: selectedFolderIds
    };
    form.removeEventListener('submit', submitHandler);
    closeGameFormModal();
    onSave && onSave(payload);
  };
  form.addEventListener('submit', submitHandler);
}

function closeGameFormModal() {
  document.getElementById('gameFormModal').style.display = 'none';
}

// ---------------- CONFIRM MODAL ---------------- //
function openConfirmModal(message, onYes) {
  document.getElementById('confirmMessage').textContent = message || 'Are you sure?';
  const modal = document.getElementById('confirmModal');
  modal.style.display = 'flex';
  const yesBtn = document.getElementById('confirmYes');
  const handler = function() {
    yesBtn.removeEventListener('click', handler);
    closeConfirmModal();
    onYes && onYes();
  };
  yesBtn.addEventListener('click', handler);
}

function closeConfirmModal() {
  document.getElementById('confirmModal').style.display = 'none';
}

// ---------------- GAME CRUD ---------------- //
async function addGame() {
  openGameFormModal({ folder_ids: currentFolder ? [currentFolder] : [] }, async (payload) => {
    try {
      await fetchJSON('/api/games/', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      // Refresh current view - either folder games or search results
      if (typeof window.isSearchMode !== 'undefined' && window.isSearchMode) {
        const searchQuery = document.getElementById('searchInput').value.trim();
        if (searchQuery) {
          searchGames(searchQuery);
        }
      } else if (currentFolder) {
        showGames(currentFolder);
      } else if (typeof loadFolders==='function') {
        loadFolders();
      }
    } catch (e) { console.error(e); }
  });
}

async function editGame(gameId) {
  try {
    const game = await fetchJSON(`/api/games/${gameId}/`);
    openGameFormModal(
      { name: game.name, number_of_players: game.number_of_players, time: game.time, materials: game.materials, description: game.description, video_link: game.video_link, folder_ids: game.folder_ids },
      async (payload) => {
        await fetchJSON(`/api/games/${gameId}/`, {
          method: 'PUT',
          body: JSON.stringify(payload)
        });
        // Refresh current view - either folder games or search results
        if (typeof window.isSearchMode !== 'undefined' && window.isSearchMode) {
          const searchQuery = document.getElementById('searchInput').value.trim();
          if (searchQuery) {
            searchGames(searchQuery);
          }
        } else if (currentFolder) {
          showGames(currentFolder);
        }
      }
    );
  } catch (e) { console.error(e); }
}

function deleteGame(gameId) {
  openConfirmModal('Are you sure you want to delete this game?', async () => {
    try {
      await fetchJSON(`/api/games/${gameId}/`, { method: 'DELETE' });
      
      // Refresh current view - either folder games or search results
      if (typeof window.isSearchMode !== 'undefined' && window.isSearchMode) {
        const searchQuery = document.getElementById('searchInput').value.trim();
        if (searchQuery) {
          searchGames(searchQuery);
        }
      } else if (currentFolder) {
        showGames(currentFolder);
      } else {
        // Fallback: remove card optimistically
        const card = document.querySelector(`[data-game-id="${gameId}"]`);
        if (card && card.parentNode) {
          card.parentNode.removeChild(card);
        }
        // If list becomes empty, show placeholder
        const container = document.getElementById('gamesContainer');
        if (container && container.children.length === 0) {
          container.innerHTML = `<p style="grid-column:1/-1; text-align:center; color: var(--muted);">No games available yet.</p>`;
        }
      }
      
      // toast
      const toast = document.getElementById('toast');
      if (toast) {
        toast.textContent = 'Game deleted';
        toast.style.display = 'block';
        setTimeout(() => { toast.style.display = 'none'; }, 1500);
      }
    } catch (e) { console.error(e); }
  });
}

// ---------------- FOLDER FORM MODAL ---------------- //
function openFolderFormModal(onSave) {
  const modal = document.getElementById('folderFormModal');
  modal.style.display = 'flex';
  const form = document.getElementById('folderForm');
  const handler = function(e) {
    e.preventDefault();
    const name = document.getElementById('folderName').value.trim();
    form.removeEventListener('submit', handler);
    closeFolderFormModal();
    onSave && onSave(name);
  };
  form.addEventListener('submit', handler);
}

function closeFolderFormModal() {
  document.getElementById('folderFormModal').style.display = 'none';
}

// Add new folder
function addFolder() {
  openFolderFormModal(async (folderName) => {
    if (!folderName) return;
    try {
      await fetchJSON('/api/folders/', { method: 'POST', body: JSON.stringify({ name: folderName }) });
      if (typeof loadFolders === 'function') loadFolders();
      const toast = document.getElementById('toast');
      if (toast) {
        toast.textContent = `Folder "${folderName}" added!`;
        toast.style.display = 'block';
        setTimeout(() => { toast.style.display = 'none'; }, 1800);
      }
    } catch (e) { console.error(e); }
  });
}
