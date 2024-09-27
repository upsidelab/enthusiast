import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { createBrowserRouter, redirect, RouterProvider } from "react-router-dom";
import { Campaign } from "@/pages/Campaign.tsx";
import { Products } from "@/pages/Products.tsx";
import { Content } from "@/pages/Content.tsx";
import Login from "@/pages/Login.tsx";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";

const protectedLoginLoader = () => {
  if (!authenticationProviderInstance.isAuthenticated()) {
    return redirect("/login");
  }

  return null;
};

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    loader: protectedLoginLoader,
    children: [
      {
        path: '/products',
        element: <Products />
      },
      {
        path: '/content',
        element: <Content />
      },
      {
        path: '/campaign',
        element: <Campaign />
      }
    ]
  },
  {
    path: "/login",
    element: <Login />
  }
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
