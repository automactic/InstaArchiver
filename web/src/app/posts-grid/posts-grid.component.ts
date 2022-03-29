import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { filter, switchMap } from 'rxjs/operators';

import { PostService, Post } from '../services/post.service';

@Component({
  selector: 'posts-grid',
  templateUrl: './posts-grid.component.html',
  styleUrls: ['./posts-grid.component.scss']
})
export class PostsGridComponent {
  postService: PostService
  posts: Post[] = []

  username?: string
  year?: string
  month?: string

  constructor(
    private route: ActivatedRoute,
    postService: PostService,
  ) {
    this.postService = postService
    this.route.queryParamMap.pipe(
      filter(queryParams => {
        return (
          queryParams.get('username') != this.username ||
          queryParams.get('year') != this.year ||
          queryParams.get('month') != this.month
        )
      }),
      switchMap(queryParams => {
        this.username = queryParams.get('username') ?? undefined
        this.year = queryParams.get('year') ?? undefined
        this.month = queryParams.get('month') ?? undefined
        return this.postService.list(0, 96, this.username, this.year, this.month)
      })
    ).subscribe(response => {
      window.scrollTo({ top: 0, behavior: 'smooth' })
      this.posts = response.posts
    })
  }
}
