import { Link } from "react-router-dom";
import { mediaUrl } from "../api";

export default function RecipeCard({ recipe }) {
  const cover = mediaUrl(recipe.cover_url);
  return (
    <Link to={`/recipe/${recipe.id}`} className="card">
      <div className="card-cover" style={cover ? { backgroundImage: `url(${cover})` } : undefined}>
        {!cover && <span>нет фото</span>}
      </div>
      <div className="card-body">
        <h3>{recipe.title}</h3>
        <p>
          {recipe.is_public ? "публичный" : "только я"}
          {recipe.saves_count ? ` · ${recipe.saves_count} сохранений` : ""}
          {recipe.is_saved ? " · в избранном" : ""}
        </p>
      </div>
    </Link>
  );
}