import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import { haptic } from "../telegram";

export default function Editor() {
  const { id } = useParams();
  const nav = useNavigate();
  const editing = Boolean(id);

  const [title, setTitle] = useState("");
  const [isPublic, setIsPublic] = useState(true);
  const [ingredients, setIngredients] = useState([""]);
  const [process, setProcess] = useState("");
  const [files, setFiles] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    api(`/recipes/${id}`).then((r) => {
      setTitle(r.title);
      setIsPublic(r.is_public);
      setIngredients(r.ingredients.length ? r.ingredients.map((i) => i.text) : [""]);
      setProcess(r.cooking_process);
    }).catch((e) => setError(e.message));
  }, [id]);

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      const payload = {
        title: title.trim(),
        cooking_process: process.trim(),
        is_public: isPublic,
        ingredients: ingredients.map((x) => x.trim()).filter(Boolean),
      };
      const recipe = editing
        ? await api(`/recipes/${id}`, { method: "PUT", json: payload })
        : await api("/recipes", { method: "POST", json: payload });

      if (files.length) {
        const form = new FormData();
        files.forEach((f) => form.append("files", f));
        await api(`/recipes/${recipe.id}/images`, { method: "POST", form });
      }
      haptic("medium");
      nav(`/recipe/${recipe.id}`);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <form className="form" onSubmit={submit}>
      <h1>{editing ? "Редактировать" : "Новый рецепт"}</h1>
      {error && <p className="error">{error}</p>}

      <label>
        Название
        <input value={title} onChange={(e) => setTitle(e.target.value)} required />
      </label>

      <label className="check">
        <input type="checkbox" checked={isPublic} onChange={(e) => setIsPublic(e.target.checked)} />
        Публиковать в общую ленту
      </label>

      <label>
        Фото
        <input type="file" accept="image/jpeg,image/png,image/webp" multiple
          onChange={(e) => setFiles([...e.target.files])} />
      </label>

      <h2>Ингредиенты</h2>
      {ingredients.map((value, i) => (
        <div className="row" key={i}>
          <input
            value={value}
            placeholder="например: мука — 200 г"
            onChange={(e) => {
              const next = [...ingredients];
              next[i] = e.target.value;
              setIngredients(next);
            }}
          />
          {ingredients.length > 1 && (
            <button type="button" onClick={() => setIngredients(ingredients.filter((_, j) => j !== i))}>
              ×
            </button>
          )}
        </div>
      ))}
      <button type="button" onClick={() => setIngredients([...ingredients, ""])}>
        + ингредиент
      </button>

      <label>
        Процесс готовки
        <textarea rows={8} value={process} onChange={(e) => setProcess(e.target.value)} required />
      </label>

      <button className="primary" type="submit">{editing ? "Сохранить" : "Создать"}</button>
    </form>
  );
}