import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Navigate, RouterProvider, createBrowserRouter } from "react-router-dom";
import "./index.css";
import { Layout } from "./components/Layout";
import { Audit } from "./pages/Audit";
import { Dashboard } from "./pages/Dashboard";
import { Login } from "./pages/Login";
import { Review } from "./pages/Review";
import { ReviewDetail } from "./pages/ReviewDetail";
import { RunDetail } from "./pages/RunDetail";
import { Runs } from "./pages/Runs";
import { Upload } from "./pages/Upload";

const router = createBrowserRouter([
  { path: "/login", element: <Login /> },
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <Navigate to="/dashboard" /> },
      { path: "dashboard", element: <Dashboard /> },
      { path: "upload", element: <Upload /> },
      { path: "runs", element: <Runs /> },
      { path: "runs/:id", element: <RunDetail /> },
      { path: "review", element: <Review /> },
      { path: "review/:id", element: <ReviewDetail /> },
      { path: "audit/:recordId", element: <Audit /> }
    ]
  }
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={new QueryClient()}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </React.StrictMode>
);
