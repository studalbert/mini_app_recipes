import { useEffect, useState } from "react";
import { api } from "../api";
import RecipeCard from "../components/RecipeCard.jsx";

export default function Profile() {
  const [tab, setTab] = useState("mine");
  const [me, setMe] = useState(null);
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/profile").then(setMe).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    const path = tab === "mine" ? "/recipes/my" : "/recipes/saved";
    api(path).then(setItems).catch((e) => setError(e.message));
  }, [tab]);

  return (
    <section>
      {me && (
        <header className="profile-head">
          {me.photo_url && <img src={me.photo_url} alt="" />}
          <div>
            <h1>{me.first_name || me.username || "Повар"}</h1>
            <p className="muted">
              {me.recipes_count} своих · {me.saved_count} добавленных
            </p>
          </div>
        </header>
      )}

      <div className="seg">
        <button className={tab === "mine" ? "on" : ""} onClick={() => setTab("mine")}>Мои</button>
        <button className={tab === "saved" ? "on" : ""} onClick={() => setTab("saved")}>Добавленные</button>
      </div>

      {error && <p className="error">{error}</p>}
      <div className="grid">
        {items.map((r) => (
          <RecipeCard key={r.id} recipe={r} />
        ))}
      </div>
    </section>
  );
}