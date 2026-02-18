import os
import asyncio
import time
from datetime import datetime
from typing import List, Optional
from functools import lru_cache

from app.models.schemas import Suggestion, PredictionResponse
from app.core.config import settings
from app.core.logs import logger

# Services
from app.services.ai import transformer_predictor, REAL_TRANSFORMER_AVAILABLE
from app.services.search import elasticsearch_predictor, LARGE_DICT_AVAILABLE, large_dictionary, ES_MANAGER_AVAILABLE, es_manager

# Optional Dependencies
try:
    from app.features.advanced_ngram import advanced_ngram
    ADVANCED_NGRAM_AVAILABLE = True
except ImportError:
    ADVANCED_NGRAM_AVAILABLE = False
    advanced_ngram = None

try:
    from app.features.advanced_context_completion import advanced_context_completer
    ADVANCED_CONTEXT_AVAILABLE = True
except ImportError:
    ADVANCED_CONTEXT_AVAILABLE = False
    advanced_context_completer = None

try:
    from app.features.advanced_ranking import advanced_ranking
    ADVANCED_RANKING_AVAILABLE = True
except ImportError:
    ADVANCED_RANKING_AVAILABLE = False
    advanced_ranking = None

try:
    from app.features.advanced_fuzzy import advanced_fuzzy
    ADVANCED_FUZZY_AVAILABLE = True
except ImportError:
    ADVANCED_FUZZY_AVAILABLE = False
    advanced_fuzzy = None

try:
    from app.features.phrase_completion import PhraseCompleter
    if LARGE_DICT_AVAILABLE and large_dictionary:
        phrase_completer = PhraseCompleter(dictionary=large_dictionary)
    else:
        phrase_completer = PhraseCompleter()
    PHRASE_COMPLETION_AVAILABLE = True
except ImportError:
    PHRASE_COMPLETION_AVAILABLE = False
    phrase_completer = None

try:
    from app.features.domain_dictionaries import domain_manager
    DOMAIN_DICT_AVAILABLE = True
except ImportError:
    DOMAIN_DICT_AVAILABLE = False
    domain_manager = None

try:
    from app.features.emoji_suggestions import emoji_suggester
    EMOJI_AVAILABLE = True
except ImportError:
    EMOJI_AVAILABLE = False
    emoji_suggester = None

try:
    from app.features.smart_templates import smart_template_manager
    SMART_TEMPLATES_AVAILABLE = True
except ImportError:
    SMART_TEMPLATES_AVAILABLE = False
    smart_template_manager = None

try:
    from app.features.context_analyzer import context_analyzer
    CONTEXT_ANALYZER_AVAILABLE = True
except ImportError:
    CONTEXT_ANALYZER_AVAILABLE = False
    context_analyzer = None

try:
    from app.features.ml_learning import ml_learning
    ML_LEARNING_AVAILABLE = True
except ImportError:
    ML_LEARNING_AVAILABLE = False
    ml_learning = None

try:
    from app.features.ml_ranking import ml_ranking
    ML_RANKING_AVAILABLE = True
except ImportError:
    ML_RANKING_AVAILABLE = False
    ml_ranking = None

try:
    from app.features.trie_index import trie_index
    TRIE_AVAILABLE = True
except ImportError:
    TRIE_AVAILABLE = False
    trie_index = None

try:
    from app.features.relevance_filter import relevance_filter
    RELEVANCE_FILTER_AVAILABLE = True
except ImportError:
    RELEVANCE_FILTER_AVAILABLE = False
    relevance_filter = None

try:
    from app.features.smart_completions import get_smart_completions
    SMART_COMPLETIONS_AVAILABLE = True
except ImportError:
    SMART_COMPLETIONS_AVAILABLE = False
    get_smart_completions = None

try:
    from app.features.common_words import is_common, first_word_common
    COMMON_WORDS_AVAILABLE = True
except ImportError:
    COMMON_WORDS_AVAILABLE = False
    is_common = lambda w: False
    first_word_common = lambda t: False
    
try:
    from app.features.medium_dictionary import medium_dictionary
    MEDIUM_DICT_AVAILABLE = True
except ImportError:
    MEDIUM_DICT_AVAILABLE = False
    medium_dictionary = None


class HybridOrchestrator:
    """Transformer ve Elasticsearch sonuçlarını birleştir"""
    
    # Backend-side debouncing (50ms cooldown per user)
    _last_request = {}
    _DEBOUNCE_MS = 50  # 50ms
    
    async def predict(
        self,
        text: str,
        context_message: str = None,
        max_suggestions: int = 50,
        use_ai: bool = True,
        use_search: bool = True,
        user_id: str = "default"
    ) -> PredictionResponse:
        """Hybrid tahmin yap"""
        
        # Backend Debouncing
        now = time.time() * 1000
        last = self._last_request.get(user_id, 0)
        if now - last < self._DEBOUNCE_MS:
             return PredictionResponse(
                suggestions=[],
                processing_time_ms=0,
                sources_used=["debounced"]
            )
        self._last_request[user_id] = now
        
        start_time = datetime.now()
        sources_used = []
        all_suggestions = []
        
        # 0. CONTEXTUAL REPLIES
        if context_message and (not text or len(text) < 3):
            replies = []
            cm_lower = context_message.lower()
            if "nasılsın" in cm_lower or "naber" in cm_lower:
                replies = ["İyiyim, teşekkürler", "Teşekkürler, siz nasılsınız?", "Her şey yolunda"]
            elif "yardım" in cm_lower:
                replies = ["Nasıl yardımcı olabilirim?", "Sorun nedir?", "Buyurun, dinliyorum"]
            elif "sipariş" in cm_lower:
                replies = ["Sipariş numaranız nedir?", "Hemen kontrol ediyorum"]
            elif "merhaba" in cm_lower or "selam" in cm_lower:
                replies = ["Merhabalar", "Selamlar", "Hoş geldiniz"]
                
            if replies:
                for reply in replies:
                    all_suggestions.append(Suggestion(
                        text=reply,
                        type="smart_reply",
                        score=50.0,
                        description="Akıllı Yanıt",
                        source="contextual_reply"
                    ))
                if not text and all_suggestions:
                     end_time = datetime.now()
                     processing_time = (end_time - start_time).total_seconds() * 1000
                     return PredictionResponse(
                        suggestions=all_suggestions,
                        processing_time_ms=processing_time,
                        sources_used=["contextual_reply"]
                    )
        
        context = None
        if ADVANCED_CONTEXT_AVAILABLE and advanced_context_completer:
             try:
                 smart_responses = advanced_context_completer.generate_smart_responses(text)
                 if smart_responses:
                     # Normalize: Dict -> Suggestion
                     all_suggestions.extend([Suggestion(**s) for s in smart_responses if isinstance(s, dict)])
                 
                 context_suggestions = advanced_context_completer.complete_with_full_context(text, max_suggestions)
                 if context_suggestions:
                     # Normalize: Dict -> Suggestion
                     all_suggestions.extend([Suggestion(**s) for s in context_suggestions if isinstance(s, dict)])
             except Exception as e:
                 logger.warning(f"Advanced Context hatasi: {e}")
        
        # YENI: ML Learning
        # if ML_LEARNING_AVAILABLE and ml_learning:
        #     try:
        #         all_suggestions = ml_learning.get_personalized_suggestions(user_id, text, all_suggestions)
        #     except Exception as e:
        #         logger.warning(f"ML Learning hatasi: {e}")

        # Paralel işlemler
        tasks = []
        
        extra_features = settings.ENABLE_HEAVY_FEATURES
        
        if use_ai and settings.USE_TRANSFORMER and extra_features:
            tasks.append(self._get_ai_predictions(text, max_suggestions, sources_used))
        
        if use_search:
            # FIX: Trailing space handling for "Next Word Prediction"
            if text.endswith(" "):
                current_prefix = ""
            else:
                words = text.split()
                current_prefix = words[-1] if words else text
            
            current_prefix = current_prefix.strip()
            
            # Sadece prefix varsa sözlük araması yap
            if len(current_prefix) >= 1:
                if TRIE_AVAILABLE and trie_index and hasattr(trie_index, 'word_count') and trie_index.word_count > 0:
                    tasks.append(self._get_trie_predictions(current_prefix, max_suggestions * 6, sources_used))
                
                tasks.append(self._get_search_predictions(current_prefix, max_suggestions * 6, sources_used))
                
                if LARGE_DICT_AVAILABLE and large_dictionary:
                    tasks.append(self._get_direct_large_dict_predictions(current_prefix, max_suggestions * 5, sources_used))
                
                if MEDIUM_DICT_AVAILABLE and medium_dictionary:
                    try:
                        # Senkron olduğu için direkt çalıştırabiliriz ama async wrapper olmadigi icin burada direkt cagiralim
                        # Ya da task yapısına uymak için basit coroutine
                        async def medium_lookup():
                            try:
                                md_results = medium_dictionary.search(current_prefix, max_suggestions)
                                if md_results:
                                    return [Suggestion(
                                        text=res['word'],
                                        type='dictionary',
                                        score=res['score'],
                                        description='Sözlük (Medium)',
                                        source='medium_dictionary'
                                    ) for res in md_results]
                            except:
                                return []
                            return []
                        tasks.append(medium_lookup())
                    except Exception as e:
                        logger.warning(f"Medium dictionary hatasi: {e}")
        
        if ADVANCED_NGRAM_AVAILABLE and advanced_ngram:
            tasks.append(self._get_ngram_predictions(text, max_suggestions * 2, sources_used))
        
        if PHRASE_COMPLETION_AVAILABLE and phrase_completer:
            tasks.append(self._get_phrase_predictions(text, max_suggestions * 2, sources_used))
        
        if DOMAIN_DICT_AVAILABLE and domain_manager:
            tasks.append(self._get_domain_predictions(text, max_suggestions * 2, sources_used))
        
        if EMOJI_AVAILABLE and emoji_suggester:
            tasks.append(self._get_emoji_predictions(text, max_suggestions * 2, sources_used))
        
        if extra_features and SMART_TEMPLATES_AVAILABLE and smart_template_manager:
            tasks.append(self._get_template_predictions(text, max_suggestions * 2, sources_used))
        
        # Task Ayrıştırma
        fast_tasks = []
        smart_tasks = []
        
        for task in tasks:
            task_str = str(task)
            if 'trie' in task_str.lower() or 'large_dict' in task_str.lower() or 'direct_large_dict' in task_str.lower() or 'search' in task_str.lower():
                fast_tasks.append(task)
            else:
                smart_tasks.append(task)
        
        # AŞAMA 1: Hızlı öneriler
        async def with_fast_timeout(task):
            try:
                return await asyncio.wait_for(task, timeout=0.1)
            except (asyncio.TimeoutError, Exception):
                return []
        
        fast_results = []
        if fast_tasks:
            fast_results = await asyncio.gather(*[with_fast_timeout(task) for task in fast_tasks], return_exceptions=True)
        
        # AŞAMA 2: Akıllı öneriler
        async def with_smart_timeout(task):
            try:
                return await asyncio.wait_for(task, timeout=0.5)
            except (asyncio.TimeoutError, Exception):
                return []
        
        smart_results = []
        if smart_tasks:
            smart_results = await asyncio.gather(*[with_smart_timeout(task) for task in smart_tasks], return_exceptions=True)
        
        results = fast_results + smart_results
        
        for result in results:
            if isinstance(result, Exception):
                continue
            if isinstance(result, list):
                # Robust Normalization: Ensure all items are Suggestion objects
                clean_result = []
                for item in result:
                    if isinstance(item, Suggestion):
                         clean_result.append(item)
                    elif isinstance(item, dict):
                        try:
                            # Convert dict to Suggestion
                            clean_result.append(Suggestion(**item))
                        except Exception:
                            # Skip invalid items
                            continue
                all_suggestions.extend(clean_result)
        
        # Smart Completions (m -> merhaba)
        if SMART_COMPLETIONS_AVAILABLE and get_smart_completions and use_search and text:
            _words = text.split()
            _lw = (_words[-1] if _words else text).strip()
            if 1 <= len(_lw) <= 4:
                comps = get_smart_completions(_lw, max_suggestions * 3)
                for d in comps:
                    all_suggestions.insert(0, Suggestion(
                        text=d["word"],
                        type=d.get("type", "smart_completion"),
                        score=d.get("score", 14.0),
                        description=d.get("description", "Öneri (öncelikli)"),
                        source=d.get("source", "smart_completions")
                    ))
                if comps and "smart_completions" not in sources_used:
                    sources_used.append("smart_completions")
        
        corrected_text = None
        
        # Context Filtreleme
        if CONTEXT_ANALYZER_AVAILABLE and context_analyzer and context and all_suggestions:
            # DEBUG
            for i, x in enumerate(all_suggestions):
                if not hasattr(x, 'text'):
                     print(f"CRASH WARNING: Item {i} is {type(x)}: {x}")
            
            try:
                all_suggestions_dict = [{'text': s.text, 'score': s.score, 'type': s.type, 'source': s.source, 'description': s.description} for s in all_suggestions]
                filtered = context_analyzer.filter_suggestions_by_context(all_suggestions_dict, context)
                if filtered and isinstance(filtered, list) and len(filtered) > 0:
                    context_suggestions = [Suggestion(**s) for s in filtered if isinstance(s, dict)]
                    for ctx_sug in context_suggestions:
                        ctx_sug.score += 2.0
                    all_suggestions = context_suggestions + [s for s in all_suggestions if s not in context_suggestions]
            except Exception:
                pass
        
        # Fuzzy Matching
        if text:
            words = text.split()
            if words:
                last_word = words[-1]
                if len(last_word) > 4 and ADVANCED_FUZZY_AVAILABLE and advanced_fuzzy and LARGE_DICT_AVAILABLE and large_dictionary:
                    try:
                        candidates = large_dictionary.words[:200]
                        fuzzy_matches = advanced_fuzzy.match(last_word, candidates, max_results=1)
                        if fuzzy_matches and fuzzy_matches[0]['confidence'] > 0.8:
                            corrected = fuzzy_matches[0]['word']
                            corrected_text = ' '.join(words[:-1] + [corrected])
                    except Exception:
                        pass
        
        # Advanced Context
        if ADVANCED_CONTEXT_AVAILABLE and advanced_context_completer and all_suggestions:
            try:
                context_suggestions = await asyncio.wait_for(
                    asyncio.to_thread(advanced_context_completer.complete_with_full_context, text, max_suggestions),
                    timeout=0.3
                )
                if context_suggestions:
                    for ctx_sug in context_suggestions[:5]:
                        if isinstance(ctx_sug, dict):
                            all_suggestions.append(Suggestion(
                                text=ctx_sug.get('text', ''),
                                type=ctx_sug.get('type', 'phrase'),
                                score=ctx_sug.get('score', 0.0),
                                description=ctx_sug.get('description', ''),
                                source=ctx_sug.get('source', 'advanced_context')
                            ))
            except (asyncio.TimeoutError, Exception):
                pass

        # Relevance Filter
        words = text.split()
        last_word = words[-1] if words else text
        should_filter = len(all_suggestions) > 5 and len(last_word) >= 2
        
        if RELEVANCE_FILTER_AVAILABLE and relevance_filter and all_suggestions and should_filter:
            try:
                suggestions_dict = [
                    {
                        'text': s.text,
                        'score': s.score,
                        'type': s.type,
                        'source': s.source,
                        'description': s.description,
                        'frequency': getattr(s, 'frequency', 1)
                    }
                    for s in all_suggestions
                ]
                filtered = relevance_filter.filter_irrelevant(suggestions_dict, text, max_suggestions * 5)
                filtered = relevance_filter.remove_duplicates(filtered)
                
                if filtered and isinstance(filtered, list) and len(filtered) > 0:
                    all_suggestions = [Suggestion(**s) for s in filtered if isinstance(s, dict)]
            except Exception:
                pass
        
        # ML Ranking
        if extra_features and ML_RANKING_AVAILABLE and ml_ranking and all_suggestions:
            try:
                context_dict = {'text': text, 'domain': 'general'}
                suggestions_dict = [
                    {
                        'text': s.text,
                        'score': s.score,
                        'type': s.type,
                        'source': s.source,
                        'frequency': getattr(s, 'frequency', 1),
                        'context_match': True,
                        'domain_match': True,
                        'grammar_match': False,
                        'semantic_score': 0.5
                    }
                    for s in all_suggestions
                ]
                ranked = ml_ranking.rank_suggestions(suggestions_dict, context_dict, user_id)
                if ranked and isinstance(ranked, list):
                    all_suggestions = [Suggestion(**s) for s in ranked if isinstance(s, dict)]
            except Exception as e:
                logger.warning(f"ML ranking hatasi: {e}")
        
        # Prefix'in kendisini filtrele
        _parts = text.split()
        _lw = (_parts[-1] if _parts else text).strip().lower()
        if _lw:
            # FIX: Handle dicts (AttributeError crash fix)
            all_suggestions = [
                s for s in all_suggestions 
                if (s.get('text', '') if isinstance(s, dict) else getattr(s, 'text', '')).strip().lower() != _lw
            ]
        
        unique_suggestions = self._merge_and_rank(all_suggestions, max_suggestions)
        
        # Fallback (Garantili Öneri)
        if not unique_suggestions and len(text.strip()) >= 1:
             words = text.split()
             last_word = words[-1] if words else text
             last_word = last_word.strip()
             
             if len(last_word) >= 1:
                try:
                    fallback_suggestions = await elasticsearch_predictor._local_search(last_word, max_suggestions * 5)
                    
                    if not fallback_suggestions and LARGE_DICT_AVAILABLE and large_dictionary:
                        try:
                            results = large_dictionary.search(last_word.lower(), max_suggestions * 5)
                            if results:
                                for result in results:
                                    fallback_suggestions.append(Suggestion(
                                        text=result['word'],
                                        type="dictionary",
                                        score=result.get('score', 8.0),
                                        description=f"Sözlük (frekans: {result.get('frequency', 0)})",
                                        source="large_dictionary_fallback"
                                    ))
                        except Exception:
                            pass
                    
                    if not fallback_suggestions:
                        for word in elasticsearch_predictor.local_dictionary[:max_suggestions * 5]:
                            word_lower = word.lower()
                            if word_lower.startswith(last_word.lower()) and word_lower != last_word.lower():
                                fallback_suggestions.append(Suggestion(
                                    text=word,
                                    type="dictionary",
                                    score=8.0,
                                    description="Sözlük (varsayılan)",
                                    source="default_dictionary"
                                ))
                                if len(fallback_suggestions) >= max_suggestions:
                                    break
                    
                    if fallback_suggestions:
                        unique_suggestions = fallback_suggestions
                        if 'local_dictionary' not in sources_used:
                            sources_used.append('local_dictionary')
                except Exception as e:
                    logger.error(f"Zorunlu arama hatasi: {e}")
        
        # Final Ranking
        # ... (Already covered mostly by _merge_and_rank, but Advanced Ranking is here)
        if ADVANCED_RANKING_AVAILABLE and advanced_ranking and unique_suggestions:
            try:
                suggestions_dict = []
                for s in unique_suggestions:
                    # Robust handling for Dict vs Object
                    try:
                        if isinstance(s, dict):
                             suggestions_dict.append(s)
                        else:
                             # Try object access
                             suggestions_dict.append({
                                'text': getattr(s, 'text', ''),
                                'score': getattr(s, 'score', 0.0),
                                'type': getattr(s, 'type', 'unknown'),
                                'source': getattr(s, 'source', 'unknown'),
                                'description': getattr(s, 'description', '')
                            })
                    except AttributeError:
                        # Fallback for dict-like objects that failed isinstance(s, dict)
                        try:
                            suggestions_dict.append({
                                'text': s.get('text', ''),
                                'score': s.get('score', 0.0),
                                'type': s.get('type', 'unknown'),
                                'source': s.get('source', 'unknown'),
                                'description': s.get('description', '')
                            })
                        except Exception:
                            continue
                ranked = advanced_ranking.rank_suggestions(suggestions_dict, context, user_id, text)
                if ranked and isinstance(ranked, list):
                    unique_suggestions = [Suggestion(**s) for s in ranked[:max_suggestions] if isinstance(s, dict)]
            except Exception as e:
                logger.warning(f"Advanced ranking hatasi: {e}")

        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return PredictionResponse(
            suggestions=unique_suggestions,
            corrected_text=corrected_text,
            processing_time_ms=round(processing_time, 2),
            sources_used=sources_used
        )
    
    async def _get_ai_predictions(self, text: str, max_suggestions: int, sources_used: List[str]):
        try:
            suggestions = await transformer_predictor.predict(text, max_suggestions)
            if suggestions:
                sources_used.append("transformer")
            return suggestions
        except Exception as e:
            logger.error(f"AI tahmin hatası: {e}")
            return []
    
    async def _get_trie_predictions(self, prefix: str, max_suggestions: int, sources_used: List[str]):
        suggestions = []
        if TRIE_AVAILABLE and trie_index and hasattr(trie_index, 'word_count') and trie_index.word_count > 0:
            try:
                results = trie_index.search(prefix, max_suggestions)
                for result in results:
                    if isinstance(result, dict):
                        suggestions.append(Suggestion(
                            text=result.get('word', ''),
                            type=result.get('type', 'dictionary'),
                            score=result.get('score', 8.0),
                            description=result.get('description', 'Sözlük (Trie)'),
                            source=result.get('source', 'trie_index')
                        ))
                if suggestions:
                    sources_used.append('trie_index')
            except Exception as e:
                logger.warning(f"Trie search hatasi: {e}")
        return suggestions
    
    async def _get_search_predictions(self, prefix: str, max_suggestions: int, sources_used: List[str]):
        try:
            prefix = prefix.strip() if prefix else ""
            if not prefix:
                return []
            
            suggestions = await elasticsearch_predictor.search(prefix, max_suggestions)
            
            if not suggestions and LARGE_DICT_AVAILABLE and large_dictionary:
                try:
                    results = large_dictionary.search(prefix.lower(), max_suggestions)
                    if results:
                        for result in results:
                            suggestions.append(Suggestion(
                                text=result['word'],
                                type="dictionary",
                                score=result.get('score', 8.0),
                                description=f"Sözlük (frekans: {result.get('frequency', 0)})",
                                source="large_dictionary"
                            ))
                except Exception:
                    pass
            
            if suggestions:
                source_name = "elasticsearch" if elasticsearch_predictor.es_client else "local_dictionary"
                if source_name not in sources_used:
                    sources_used.append(source_name)
            
            return suggestions
        except Exception as e:
            logger.error(f"Sözlük arama hatası: {e}")
            return []

    async def _get_direct_large_dict_predictions(self, prefix: str, max_suggestions: int, sources_used: List[str]):
        suggestions = []
        try:
            if LARGE_DICT_AVAILABLE and large_dictionary:
                results = large_dictionary.search(prefix.lower(), max_suggestions)
                if results:
                    for result in results:
                        suggestions.append(Suggestion(
                            text=result['word'],
                            type="dictionary",
                            score=result.get('score', 9.0),
                            description=f"Sözlük (frekans: {result.get('frequency', 0)})",
                            source="large_dictionary_direct"
                        ))
                    if suggestions and 'large_dictionary_direct' not in sources_used:
                        sources_used.append('large_dictionary_direct')
        except Exception as e:
            logger.warning(f"Direct large dict search hatasi: {e}")
        return suggestions

    async def _get_ngram_predictions(self, text: str, max_suggestions: int, sources_used: List[str]):
        try:
            if ADVANCED_NGRAM_AVAILABLE and advanced_ngram and hasattr(advanced_ngram, 'predict_next_word'):
                results = advanced_ngram.predict_next_word(text, max_suggestions)
                suggestions = []
                if results and isinstance(results, list):
                    for result in results:
                        if not isinstance(result, dict):
                            continue
                        txt = result.get('text') or result.get('word', '')
                        if not txt:
                            continue
                        suggestions.append(Suggestion(
                            text=txt,
                            type=result.get('type', 'ngram'),
                            score=result.get('score', 8.5),
                            description=result.get('description', 'N-gram tahmini'),
                            source=result.get('source', 'advanced_ngram')
                        ))
                if suggestions:
                    sources_used.append("advanced_ngram")
                return suggestions
            return []
        except Exception as e:
            logger.warning(f"N-gram prediction hatasi: {e}")
            return []

    async def _get_phrase_predictions(self, text: str, max_suggestions: int, sources_used: List[str]):
        try:
            if PHRASE_COMPLETION_AVAILABLE and phrase_completer and hasattr(phrase_completer, 'complete_phrase'):
                results = phrase_completer.complete_phrase(text, max_suggestions)
                suggestions = []
                if results and isinstance(results, list):
                    for result in results:
                        if isinstance(result, dict) and 'text' in result:
                            suggestions.append(Suggestion(
                                text=result['text'],
                                type=result.get('type', 'phrase'),
                                score=result.get('score', 8.0),
                                description=result.get('description', 'Cümle tamamlama'),
                                source=result.get('source', 'phrase_completion')
                            ))
                if suggestions:
                    sources_used.append("phrase_completion")
                return suggestions
            return []
        except Exception as e:
            logger.warning(f"Phrase completion hatasi: {e}")
            return []
    
    async def _get_domain_predictions(self, text: str, max_suggestions: int, sources_used: List[str]):
        try:
            if DOMAIN_DICT_AVAILABLE and domain_manager and hasattr(domain_manager, 'get_suggestions'):
                words = text.split()
                last_word = words[-1] if words else text
                context = None
                if CONTEXT_ANALYZER_AVAILABLE and context_analyzer and hasattr(context_analyzer, 'analyze'):
                    try:
                        context_analysis = context_analyzer.analyze(text)
                        if context_analysis and isinstance(context_analysis, dict):
                            if context_analysis.get('topic') in ['customer_service', 'technical', 'ecommerce']:
                                context = context_analysis.get('topic')
                    except Exception:
                        pass
                
                results = domain_manager.get_suggestions(last_word, context, max_suggestions)
                suggestions = []
                if results and isinstance(results, list):
                    for result in results:
                        if isinstance(result, dict) and 'text' in result:
                            suggestions.append(Suggestion(
                                text=result['text'],
                                type=result.get('type', 'domain'),
                                score=result.get('score', 8.5),
                                description=result.get('description', 'Domain sözlüğü'),
                                source=result.get('source', 'domain_dict')
                            ))
                if suggestions:
                    sources_used.append("domain_dict")
                return suggestions
            return []
        except Exception as e:
            logger.warning(f"Domain dictionary hatasi: {e}")
            return []
    
    async def _get_emoji_predictions(self, text: str, max_suggestions: int, sources_used: List[str]):
        try:
            if EMOJI_AVAILABLE and emoji_suggester and hasattr(emoji_suggester, 'suggest_emojis'):
                results = emoji_suggester.suggest_emojis(text, max_suggestions)
                suggestions = []
                if results and isinstance(results, list):
                    for result in results:
                        if isinstance(result, dict) and 'text' in result:
                            suggestions.append(Suggestion(
                                text=result['text'],
                                type=result.get('type', 'emoji'),
                                score=result.get('score', 8.0),
                                description=result.get('description', 'Emoji önerisi'),
                                source=result.get('source', 'emoji')
                            ))
                if suggestions:
                    sources_used.append("emoji")
                return suggestions
            return []
        except Exception as e:
            logger.warning(f"Emoji suggestion hatasi: {e}")
            return []
    
    async def _get_template_predictions(self, text: str, max_suggestions: int, sources_used: List[str]):
        try:
            if SMART_TEMPLATES_AVAILABLE and smart_template_manager and hasattr(smart_template_manager, 'get_templates'):
                if text.startswith('/') or any(word in text.lower() for word in ['sipariş', 'müşteri', 'api', 'database']):
                    results = smart_template_manager.get_templates(text, max_suggestions)
                    suggestions = []
                    if results and isinstance(results, list):
                        for result in results:
                            if isinstance(result, dict) and 'text' in result:
                                suggestions.append(Suggestion(
                                    text=result['text'],
                                    type=result.get('type', 'template'),
                                    score=result.get('score', 9.0),
                                    description=result.get('description', 'Akıllı şablon'),
                                    source=result.get('source', 'smart_templates')
                                ))
                    if suggestions:
                        sources_used.append("smart_templates")
                    return suggestions
            return []
        except Exception as e:
            logger.warning(f"Smart template hatasi: {e}")
            return []

    def _merge_and_rank(self, suggestions: List[Suggestion], max_suggestions: int) -> List[Suggestion]:
        if not suggestions:
            return []
        
        seen = set()
        unique_suggestions = []
        
        for sug in suggestions:
            if not sug or not sug.text:
                continue
            key = sug.text.lower().strip()
            if not key:
                continue
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(sug)
            else:
                existing = next((s for s in unique_suggestions if s.text.lower() == key), None)
                if existing:
                    existing.score = max(existing.score, sug.score) + 0.5
        
        if COMMON_WORDS_AVAILABLE and is_common and first_word_common:
            for s in unique_suggestions:
                t = (s.text or "").strip()
                if not t:
                    continue
                if " " not in t and is_common(t):
                    s.score += 3.5
                elif first_word_common(t):
                    s.score += 2.0
        
        unique_suggestions.sort(key=lambda x: x.score, reverse=True)
        return unique_suggestions[:max_suggestions]

orchestrator = HybridOrchestrator()
