import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { PostDetailComponent } from './post-detail/post-detail.component';
import { PostsGridComponent } from './posts-grid/posts-grid.component';

const routes: Routes = [
  { path: 'posts', component: PostsGridComponent, children: [
    { path: ':shortcode', component: PostDetailComponent },
  ]},
  { path: ':username', component: PostsGridComponent, children: [
    { path: ':shortcode', component: PostDetailComponent },
  ]},
  { path: '**', redirectTo: '/posts'},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
