import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, mediaUrl } from "../api";
import { haptic } from "../telegram";

export default function Recipe() {
  const { id } = useParams();
  const nav = useNavigate();
  const [me, setMe] = useState(null);
  const [recipe, setRecipe] = useState(null);
  const [error, setError] = useState("");

  async function load() {
    const [user, data] = await Promise.all([api("/auth/me"), api(`/recipes/${id}`)]);
    setMe(user);
    setRecipe(data);
  }

  useEffect(() => {
    load().catch((e) => setError(e.message));
  }, [id]);

  if (error) return <p className="error">{error}</p>;
  if (!recipe) return <p className="muted">Загрузка…</p>;

  const mine = me && recipe.author_id === me.id;

  async function toggleSave() {
    haptic();
    if (recipe.is_saved) await api(`/recipes/${id}/save`, { method: "DELETE" });
    else await api(`/recipes/${id}/save`, { method: "POST" });
    await load();
  }

  async function remove() {
    if (!confirm("Удалить рецепт?")) return;
    await api(`/recipes/${id}`, { method: "DELETE" });
    nav("/profile");
  }

  return (
    <article className="recipe">
      {recipe.images?.[0] && (
        <img className="hero" src={mediaUrl(recipe.images[0].url)} alt="" />
      )}
      <h1>{recipe.title}</h1>
      <p className="muted">{recipe.is_public ? "В общей ленте" : "Приватный"}</p>

      <div className="actions">
        {!mine && (
          <button onClick={toggleSave}>{recipe.is_saved ? "Убрать из своих" : "Добавить к себе"}</button>
        )}
        {mine && (
          <>
            <Link to={`/edit/${id}`} className="btn">Редактировать</Link>
            <button className="danger" onClick={remove}>Удалить</button>
          </>
        )}
      </div>

      <h2>Ингредиенты</h2>
      <ul>
        {recipe.ingredients.map((i) => (
          <li key={i.id}>{i.text}</li>
        ))}
      </ul>

      <h2>Как готовить</h2>
      <p className="process">{recipe.cooking_process}</p>
    </article>
  );
}