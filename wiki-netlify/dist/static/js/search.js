let searchIndex=null;let searchTimeout=null;async function loadSearchIndex(){if(searchIndex)return searchIndex;try{const response=await fetch('/search-index.json');searchIndex=await response.json();return searchIndex;}catch(error){console.error('Failed to load search index:',error);return[];}}
function highlightText(text,query){if(!query)return text;const terms=query.toLowerCase().split(/\s+/).filter(term=>term.length>0);let highlighted=text;terms.forEach(term=>{const regex=new RegExp(`(${escapeRegex(term)})`,'gi');highlighted=highlighted.replace(regex,'<mark class="search-highlight">$1</mark>');});return highlighted;}
function escapeRegex(str){return str.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');}
function search(query,limit=10){if(!searchIndex||!query||query.trim().length<2){return[];}
const queryLower=query.toLowerCase();const terms=queryLower.split(/\s+/).filter(term=>term.length>0);const results=searchIndex.map(item=>{let score=0;const titleLower=item.title.toLowerCase();const contentLower=item.content.toLowerCase();terms.forEach(term=>{if(titleLower.includes(term)){score+=10;if(titleLower===term){score+=20;}}
const contentMatches=(contentLower.match(new RegExp(term,'g'))||[]).length;score+=contentMatches;});return{...item,score};}).filter(item=>item.score>0).sort((a,b)=>b.score-a.score).slice(0,limit);return results;}
function renderQuickSearchResults(results,query){const container=document.getElementById('search-results');if(!container)return;if(results.length===0){container.innerHTML='<div class="search-result-item"><div class="search-result-preview">Ничего не найдено</div></div>';container.classList.add('active');return;}
const html=results.map(result=>{const highlightedTitle=highlightText(result.title,query);const highlightedPreview=highlightText(result.content.substring(0,150),query);return`
            <a href="${result.url}" class="search-result-item">
                <div class="search-result-title">${highlightedTitle}</div>
                <div class="search-result-preview">${highlightedPreview}...</div>
                <div class="search-result-category">${result.category}</div>
            </a>
        `;}).join('');container.innerHTML=html;container.classList.add('active');}
function renderFullSearchResults(results,query){const container=document.getElementById('search-results-container');if(!container)return;if(results.length===0){container.innerHTML='<p class="search-hint">Ничего не найдено. Попробуйте другой запрос.</p>';return;}
const html=results.map(result=>{const highlightedTitle=highlightText(result.title,query);const highlightedPreview=highlightText(result.content.substring(0,300),query);return`
            <div class="search-result-card">
                <h3><a href="${result.url}">${highlightedTitle}</a></h3>
                <div class="search-result-meta">Категория: ${result.category}</div>
                <div class="search-result-preview">${highlightedPreview}...</div>
            </div>
        `;}).join('');container.innerHTML=html;}
function setupQuickSearch(){const input=document.getElementById('quick-search');if(!input)return;input.addEventListener('focus',()=>{loadSearchIndex();},{once:true});input.addEventListener('input',(e)=>{const query=e.target.value.trim();clearTimeout(searchTimeout);if(query.length<2){const container=document.getElementById('search-results');if(container){container.classList.remove('active');}
return;}
searchTimeout=setTimeout(async()=>{await loadSearchIndex();const results=search(query,5);renderQuickSearchResults(results,query);},300);});document.addEventListener('click',(e)=>{const container=document.getElementById('search-results');if(container&&!container.contains(e.target)&&e.target!==input){container.classList.remove('active');}});input.addEventListener('keydown',(e)=>{if(e.key==='Enter'){const container=document.getElementById('search-results');const firstResult=container?.querySelector('.search-result-item');if(firstResult){window.location.href=firstResult.href;}}});}
function setupFullSearch(){const input=document.getElementById('search-input');if(!input)return;input.addEventListener('focus',()=>{loadSearchIndex();},{once:true});input.addEventListener('input',(e)=>{const query=e.target.value.trim();clearTimeout(searchTimeout);if(query.length<2){const container=document.getElementById('search-results-container');if(container){container.innerHTML='<p class="search-hint">Начните вводить запрос для поиска по статьям</p>';}
return;}
searchTimeout=setTimeout(async()=>{await loadSearchIndex();const results=search(query,20);renderFullSearchResults(results,query);},300);});}
document.addEventListener('DOMContentLoaded',()=>{setupQuickSearch();setupFullSearch();});