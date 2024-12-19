import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";
import { UsersList } from "@/components/users/users-list.tsx";

export function UsersIndex() {
  return (
    <PageMain>
      <PageHeading title="Manage Users" description="Create user accounts to control access to data sets." />
      <UsersList />
    </PageMain>
  )
}
