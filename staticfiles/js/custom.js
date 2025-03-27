document.addEventListener('DOMContentLoaded', function() {
    // Add click handlers for menu items
    const menuItems = document.querySelectorAll('.nav-sidebar .has-treeview > .nav-link');

    menuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();

            const parent = this.parentElement;
            const isOpen = parent.classList.contains('menu-open');

            // Close all other menus
            const otherMenus = document.querySelectorAll('.nav-sidebar .has-treeview.menu-open');
            otherMenus.forEach(menu => {
                if (menu !== parent) {
                    menu.classList.remove('menu-open');
                }
            });

            // Toggle current menu
            parent.classList.toggle('menu-open');
        });
    });

    // Auto-expand menu for active items
    const activeItems = document.querySelectorAll('.nav-sidebar .nav-treeview .nav-link.active');
    activeItems.forEach(item => {
        let parent = item.closest('.has-treeview');
        if (parent) {
            parent.classList.add('menu-open');
        }
    });
});

// admin.js

// Wait for document to be ready
document.addEventListener('DOMContentLoaded', function() {

    // 1. Quick Action Panel
    function initializeQuickActionPanel() {
        const actionButton = `
            <div class="quick-actions-toggle">
                <button class="btn-floating">
                    <i class="fas fa-bolt"></i>
                </button>
            </div>
        `;

        const actionPanel = `
            <div class="quick-actions-panel">
                <div class="quick-actions-header">
                    <h5>Quick Actions</h5>
                    <button class="close-panel"><i class="fas fa-times"></i></button>
                </div>
                <div class="quick-actions-content">
                    <div class="quick-action-item" data-action="add">
                        <i class="fas fa-plus"></i>
                        <span>New Entry</span>
                    </div>
                    <div class="quick-action-item" data-action="export">
                        <i class="fas fa-file-export"></i>
                        <span>Export Data</span>
                    </div>
                    <div class="quick-action-item" data-action="filter">
                        <i class="fas fa-filter"></i>
                        <span>Quick Filter</span>
                    </div>
                    <div class="quick-action-item" data-action="bookmark">
                        <i class="fas fa-bookmark"></i>
                        <span>Bookmark</span>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', actionButton + actionPanel);
    }

    // 2. Enhanced Search with Filters
    function enhanceSearch() {
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.addEventListener('input', debounce(function(e) {
                const searchTerm = e.target.value;
                highlightMatchingRows(searchTerm);
            }, 300));
        }
    }

    // 3. Table Row Actions
    function initializeTableActions() {
        const tableRows = document.querySelectorAll('tbody tr');
        tableRows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                const actions = this.querySelector('.row-actions');
                if (actions) actions.style.opacity = '1';
            });
            row.addEventListener('mouseleave', function() {
                const actions = this.querySelector('.row-actions');
                if (actions) actions.style.opacity = '0';
            });
        });
    }

    // 4. Bulk Actions Enhancement
    function enhanceBulkActions() {
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        const bulkActionBar = `
            <div class="bulk-action-bar">
                <span class="selected-count">0 items selected</span>
                <div class="bulk-actions">
                    <button class="bulk-action" data-action="delete">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                    <button class="bulk-action" data-action="export">
                        <i class="fas fa-file-export"></i> Export
                    </button>
                    <button class="bulk-action" data-action="tag">
                        <i class="fas fa-tag"></i> Tag
                    </button>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', bulkActionBar);
    }

    // 5. Keyboard Shortcuts
    function initializeKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + / to show shortcuts panel
            if ((e.ctrlKey || e.metaKey) && e.key === '/') {
                showShortcutsPanel();
            }
            // Ctrl/Cmd + F to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                document.querySelector('.search-input')?.focus();
            }
        });
    }

    // 6. Recent Actions Memory
    function trackRecentActions() {
        let recentActions = JSON.parse(localStorage.getItem('recentActions') || '[]');
        const action = {
            type: 'page_visit',
            url: window.location.pathname,
            timestamp: new Date().toISOString()
        };
        recentActions.unshift(action);
        recentActions = recentActions.slice(0, 10); // Keep only last 10 actions
        localStorage.setItem('recentActions', JSON.stringify(recentActions));
    }

    // 7. Smart Filters
    function initializeSmartFilters() {
        const filterPanel = `
            <div class="smart-filters">
                <div class="filter-group">
                    <label>Quick Filters</label>
                    <button class="filter-chip" data-period="today">Today</button>
                    <button class="filter-chip" data-period="week">This Week</button>
                    <button class="filter-chip" data-period="month">This Month</button>
                </div>
                <div class="filter-group">
                    <label>Status</label>
                    <button class="filter-chip" data-status="active">Active</button>
                    <button class="filter-chip" data-status="pending">Pending</button>
                    <button class="filter-chip" data-status="archived">Archived</button>
                </div>
            </div>
        `;
        document.querySelector('.content-header')?.insertAdjacentHTML('beforeend', filterPanel);
    }

    // 8. Floating Notes
    function initializeFloatingNotes() {
        const noteButton = `
            <div class="floating-note-toggle">
                <button class="btn-floating">
                    <i class="fas fa-sticky-note"></i>
                </button>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', noteButton);
    }

    // Initialize all features
    initializeQuickActionPanel();
    enhanceSearch();
    initializeTableActions();
    enhanceBulkActions();
    initializeKeyboardShortcuts();
    trackRecentActions();
    initializeSmartFilters();
    initializeFloatingNotes();
});

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function highlightMatchingRows(term) {
    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const match = text.includes(term.toLowerCase());
        row.style.display = match ? '' : 'none';
        if (match && term) {
            row.style.backgroundColor = 'rgba(107, 92, 168, 0.1)';
        } else {
            row.style.backgroundColor = '';
        }
    });
}