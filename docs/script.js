document.addEventListener('DOMContentLoaded', () => {
    const postsContainer = document.getElementById('posts-container');
    const loadingState = document.getElementById('loading-state');
    const emptyState = document.getElementById('empty-state');
    const siteFilter = document.getElementById('site-filter');
    const lastUpdated = document.getElementById('last-updated');

    let allPosts = [];

    // Fetch data
    fetch('data/posts.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            allPosts = data;
            populateFilterOptions();
            renderPosts(allPosts);
            updateLastModified();
        })
        .catch(error => {
            console.error('Error fetching posts:', error);
            loadingState.innerHTML = `
                <div class="text-red-500">
                    <i class="fas fa-exclamation-circle text-3xl mb-3"></i>
                    <p>데이터를 불러오는데 실패했습니다.</p>
                </div>
            `;
        });

    // Handle filter change
    siteFilter.addEventListener('change', (e) => {
        const selectedSite = e.target.value;
        if (selectedSite === 'all') {
            renderPosts(allPosts);
        } else {
            const filteredPosts = allPosts.filter(post => post.site_name === selectedSite);
            renderPosts(filteredPosts);
        }
    });

    function populateFilterOptions() {
        const sites = [...new Set(allPosts.map(post => post.site_name))];
        sites.forEach(site => {
            const option = document.createElement('option');
            option.value = site;
            option.textContent = site;
            siteFilter.appendChild(option);
        });
    }

    function renderPosts(posts) {
        loadingState.style.display = 'none';
        postsContainer.innerHTML = '';

        if (posts.length === 0) {
            emptyState.classList.remove('hidden');
            return;
        }

        emptyState.classList.add('hidden');

        posts.forEach(post => {
            const isNew = isPostNew(post.scraped_at);

            const card = document.createElement('a');
            card.href = post.link;
            card.target = '_blank';
            card.rel = 'noopener noreferrer';
            card.className = "block bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md hover:border-blue-300 transition-all duration-200 overflow-hidden flex flex-col h-full group";

            card.innerHTML = `
                <div class="p-5 flex-1 flex flex-col">
                    <div class="flex justify-between items-start mb-3">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            ${escapeHtml(post.site_name)}
                        </span>
                        ${isNew ? '<span class="flex h-2.5 w-2.5 relative"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span><span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500"></span></span>' : ''}
                    </div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors line-clamp-2">
                        ${escapeHtml(post.title)}
                    </h3>
                    <div class="mt-auto pt-4 flex items-center text-sm text-gray-500">
                        <i class="far fa-calendar-alt mr-1.5"></i>
                        ${escapeHtml(post.date)}
                        <span class="ml-3 text-xs text-gray-400" title="수집 일시">
                            <i class="fas fa-download mr-1"></i>${post.scraped_at ? new Date(post.scraped_at).toLocaleDateString('ko-KR') : '-'}
                        </span>
                    </div>
                </div>
            `;
            postsContainer.appendChild(card);
        });
    }

    function isPostNew(scrapedAtStr) {
        if (!scrapedAtStr) return false;
        const scrapedAt = new Date(scrapedAtStr);
        const now = new Date();
        const diffHours = (now - scrapedAt) / (1000 * 60 * 60);
        return diffHours < 24; // Consider posts scraped within 24 hours as "new"
    }

    function updateLastModified() {
        if (allPosts.length > 0) {
            const mostRecentStr = allPosts.reduce((latest, post) => {
                if (!post.scraped_at) return latest;
                return post.scraped_at > latest ? post.scraped_at : latest;
            }, '');

            if (mostRecentStr) {
                const date = new Date(mostRecentStr);
                lastUpdated.innerHTML = `<i class="fas fa-clock mr-2"></i> 뉴스 최근 수집 일시: ${date.toLocaleString('ko-KR')}`;
            }
        }
    }

    function escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
            .toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
