from __future__ import annotations

from collections import Counter
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis_history import AnalysisHistory
from app.nlp.preprocessing.stopwords import remove_stopwords_tokens
from app.schemas.dashboard import SentimentLabel


def _tokenize(texts: Iterable[str]) -> list[str]:
	words: list[str] = []
	for text in texts:
		words.extend(remove_stopwords_tokens(text.split(), use_default_stopwords=True))
	return words


async def get_keywords(
	db: AsyncSession,
	*,
	user_id: int,
	sentiment: SentimentLabel | None,
	job_id: str | None,
	top: int,
) -> list[dict[str, int | str]]:
	query = select(AnalysisHistory.input_text).where(AnalysisHistory.user_id == user_id)
	if sentiment:
		query = query.where(AnalysisHistory.result_label == sentiment)
	if job_id:
		query = query.where(AnalysisHistory.job_id == job_id)

	result = await db.execute(query)
	print(result.all())
	texts = [row[0] for row in result.all() if row and isinstance(row[0], str)]
	if not texts:
		return []

	counts = Counter(_tokenize(texts))
	items = [
		{"word": word, "count": count}
		for word, count in counts.most_common(max(top, 1))
	]
	return items
