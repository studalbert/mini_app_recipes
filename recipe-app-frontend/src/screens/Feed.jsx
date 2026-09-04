import { useEffect, useState } from "react";
import { api } from "../api";
import RecipeCard from "../components/RecipeCard.jsx";

export default function Feed() {
  const [q, setQ] = useState("");
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const t = setTimeout(() => {
      setError("");
      const query = q.trim() ? `?q=${encodeURIComponent(q.trim())}` : "";
      api(`/recipes${query}`)
        .then(setItems)
        .catch((e) => setError(e.message));
    }, 250);
    return () => clearTimeout(t);
  }, [q]);

  return (
    <section>
      <header className="page-head">
        <h1>Рецепты</h1>
        <input
          className="search"
          placeholder="Найти по названию"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </header>
      {error && <p className="error">{error}</p>}
      <div className="grid">
        {items.map((r) => (
          <RecipeCard key={r.id} recipe={r} />
        ))}
      </div>
      {!error && items.length === 0 && <p className="muted">Пока пусто</p>}
    </section>
  );
}