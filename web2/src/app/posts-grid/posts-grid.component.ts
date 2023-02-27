import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Observable } from 'rxjs';
import { filter, switchMap, tap } from 'rxjs/operators';

import { PostService, ListPostsResponse } from '../services/post.service';


@Component({
  selector: 'app-posts-grid',
  templateUrl: './posts-grid.component.html',
  styleUrls: ['./posts-grid.component.scss']
})
export class PostsGridComponent {
  username?: string;
  response$?: Observable<ListPostsResponse>;
  postService: PostService;

  constructor(private route: ActivatedRoute, postService: PostService) {
    this.postService = postService
    this.response$ = this.route.paramMap.pipe(
      filter(params => {
        return this.username == undefined || params.get('username') != this.username
      }),
      tap(params => {
        this.username = params.get('username') ?? undefined
      }),
      switchMap(params => {
        return postService.list(0, 100, this.username)
      })
    )
  }
}
