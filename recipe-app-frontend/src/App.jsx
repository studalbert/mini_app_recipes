import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import Feed from "./screens/Feed.jsx";
import Recipe from "./screens/Recipe.jsx";
import Editor from "./screens/Editor.jsx";
import Profile from "./screens/Profile.jsx";

export default function App() {
  return (
    <div className="app">
      <div className="app-body">
        <Routes>
          <Route path="/" element={<Feed />} />
          <Route path="/recipe/:id" element={<Recipe />} />
          <Route path="/new" element={<Editor />} />
          <Route path="/edit/:id" element={<Editor />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
      <nav className="tabbar">
        <NavLink to="/" end>Лента</NavLink>
        <NavLink to="/new" className="tab-plus">+</NavLink>
        <NavLink to="/profile">Профиль</NavLink>
      </nav>
    </div>
  );
}