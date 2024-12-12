import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import { createBrowserRouter, redirect, RouterProvider } from "react-router-dom";
import { History } from "@/pages/History.tsx";
import { Campaign } from "@/pages/Campaign.tsx";
import { Products } from "@/pages/Products.tsx";
import { Documents } from "@/pages/Documents.tsx";
import Login from "@/pages/Login.tsx";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { ApiConnection } from "@/pages/ApiConnection.tsx";
import { Settings } from "@/pages/Settings.tsx";
import { Docs } from "@/pages/Docs.tsx";
import { Billing } from "@/pages/Billing.tsx";
import { NoDataSets } from "@/pages/NoDataSets.tsx";
import { ApiClient } from "@/lib/api.ts";
import CreateDataSet from "@/pages/CreateDataSet.tsx";
import { ManageDataSets } from "@/pages/ManageDataSets.tsx";
import { ManageDataSetUsers } from "@/pages/ManageDataSetUsers.tsx";

const api = new ApiClient(authenticationProviderInstance);

const protectedLoginLoader = async () => {
  if (!authenticationProviderInstance.isAuthenticated()) {
    return redirect("/login");
  }

  const apiDataSets = await api.getDataSets();
  if (apiDataSets.length === 0) {
    return redirect("/no-data-sets");
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
        path: '/documents',
        element: <Documents />
      },
      {
        path: '/data-sets',
        element: <ManageDataSets />
      },
      {
        path: '/data-sets/new',
        element: <CreateDataSet />
      },
      {
        path: '/data-sets/:id/users',
        element: <ManageDataSetUsers />
      },
      {
        path: "/",
        element: <Campaign />
      },
      {
        path: '/ask/chat/:id?',
        element: <Campaign />
      },
      {
        path: '/ask/history',
        element: <History />
      },
      {
        path: '/api-connection',
        element: <ApiConnection />
      },
      {
        path: '/docs',
        element: <Docs />
      },
      {
        path: '/settings',
        element: <Settings />
      },
      {
        path: '/billing',
        element: <Billing />
      }
    ]
  },
  {
    path: "/login",
    element: <Login />
  },
  {
    path: "/no-data-sets",
    element: <NoDataSets />
  }
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
