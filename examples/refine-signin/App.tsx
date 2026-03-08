import { Refine } from "@refinedev/core";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { authProvider } from "./authProvider";
import { CallbackPage } from "./CallbackPage";
import { LoginPage } from "./LoginPage";

// Example wiring — adapt to your existing <Refine /> setup.
export function App() {
  return (
    <BrowserRouter>
      <Refine authProvider={authProvider}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/callback" element={<CallbackPage />} />
          {/* your protected routes here */}
        </Routes>
      </Refine>
    </BrowserRouter>
  );
}
