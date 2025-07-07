import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import { createBrowserRouter, redirect, RouterProvider } from "react-router-dom";
import { ChatHistory } from "@/pages/data-sets/(id)/history.tsx";
import { Chat } from "@/pages/data-sets/(id)/chat/(id)/index.tsx";
import { ProductsIndex } from "@/pages/data-sets/(id)/products/index.tsx";
import { DocumentsIndex } from "@/pages/data-sets/(id)/documents/index.tsx";
import { LoginPage } from "@/pages/login.tsx";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { ApiConnectionIndex } from "@/pages/service-accounts/index.tsx";
import { NoDataSets } from "@/pages/no-data-sets.tsx";
import { ApiClient } from "@/lib/api.ts";
import { NewDataSet } from "@/pages/data-sets/new.tsx";
import { DataSetsIndex } from "@/pages/data-sets";
import { IndexDataSetUsers } from "@/pages/data-sets/(id)/users.tsx";
import { IndexDataSetSources } from "@/pages/data-sets/(id)/sources.tsx";
import { ConfigureDataSetProductSource } from "@/pages/data-sets/(id)/product-sources/(id)/config.tsx";
import { ConfigureDataSetDocumentSource } from "@/pages/data-sets/(id)/document-sources/(id)/config.tsx";
import { UsersIndex } from "@/pages/users";
import { OnboardingIndex } from "@/pages/onboarding";
import { NewChat } from "@/pages/data-sets/(id)/chat/new/(agent)/index.tsx";

const api = new ApiClient(authenticationProviderInstance);

const protectedLoginLoader = async () => {
  if (!authenticationProviderInstance.isAuthenticated()) {
    return redirect("/login");
  }

  const apiDataSets = await api.dataSets().getDataSets();
  if (!apiDataSets) {
    return redirect("/login");
  }

  if (apiDataSets.length === 0) {
    const accountData = await api.getAccount();
    if (accountData.isStaff) {
      return redirect("/onboarding");
    } else {
      return redirect("/no-data-sets");
    }
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
        path: '/data-sets/:id/products',
        element: <ProductsIndex />
      },
      {
        path: '/data-sets/:id/documents',
        element: <DocumentsIndex />
      },
      {
        path: "/",
        element: <NewChat />
      },
      {
        path: '/data-sets/:id/chat/new/:agent',
        element: <NewChat />
      },
      {
        path: '/data-sets/:id/chat/:chatId',
        element: <Chat />
      },
      {
        path: '/data-sets/:id/history',
        element: <ChatHistory />
      },
      {
        path: '/data-sets',
        element: <DataSetsIndex />
      },
      {
        path: '/data-sets/new',
        element: <NewDataSet />
      },
      {
        path: '/data-sets/:id/users',
        element: <IndexDataSetUsers />
      },
      {
        path: '/data-sets/:id/sources',
        element: <IndexDataSetSources />
      },      
      {
        path: '/data-sets/:dataSetId/product-sources/:productSourceId',
        element: <ConfigureDataSetProductSource />
      },      
      {
        path: '/data-sets/:dataSetId/document-sources/:documentSourceId',
        element: <ConfigureDataSetDocumentSource />
      },
      {
        path: '/service-accounts',
        element: <ApiConnectionIndex />
      },
      {
        path: '/users',
        element: <UsersIndex />
      }
    ]
  },
  {
    path: "/login",
    element: <LoginPage />
  },
  {
    path: "/no-data-sets",
    element: <NoDataSets />
  },
  {
    path: "/onboarding",
    element: <OnboardingIndex />
  }
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
