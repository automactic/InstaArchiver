import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { ArchiveComponent } from './archive/archive.component';
import { PostsComponent } from './posts/posts.component';
import { ProfileDetailComponent } from './profile-detail/profile-detail.component';
import { ProfilesComponent } from './profiles/profiles.component';

const routes: Routes = [
  { path: 'archive', component: ArchiveComponent },
  { path: 'posts', component: PostsComponent },
  { path: 'profiles', component: ProfilesComponent, children: [
    { path: ':username', component: ProfileDetailComponent }
  ] },
  { path: '',   redirectTo: '/posts', pathMatch: 'full' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
