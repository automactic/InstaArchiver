import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { switchMap } from 'rxjs/operators';

import { Post, PostItem, PostService } from '../services/post.service';
import { ProfileService } from '../services/profile.service';


@Component({
  selector: 'app-posts',
  templateUrl: './posts.component.html',
  styleUrls: ['./posts.component.scss']
})
export class PostsComponent {
  postService: PostService;
  profileService: ProfileService;

  username?: string;
  year?: string;
  loading = false;
  posts: Post[] = [];
  
  constructor(private route: ActivatedRoute, private router: Router, postService: PostService, profileService: ProfileService) {
    this.postService = postService;
    this.profileService = profileService;
    this.route.queryParamMap.pipe(
      switchMap(queryParam => {
        this.username = queryParam.get("username") ?? undefined;
        this.year = queryParam.get("year") ?? undefined;
        return this.postService.list(0, 5, this.username, this.year);
      })
    ).subscribe(response => {
      window.scrollTo({ top: 0, behavior: 'smooth'});
      this.posts = response.posts;
    })
  }

  selectedProfileChanged(username: string) {
    this.router.navigate([], { 
      relativeTo: this.route, 
      queryParams: { username: username}, 
      queryParamsHandling: 'merge' 
    });
  }

  selectedYearChanged(year: string) {
    this.router.navigate([], { 
      relativeTo: this.route, 
      queryParams: { year: year}, 
      queryParamsHandling: 'merge' 
    });
  }

  loadNext() {
    if (this.loading) { return }
    this.loading = true;
    this.postService.list(this.posts.length, 5, this.username, this.year).subscribe( response_data => {
      this.posts.push(...response_data.posts);
      this.loading = false;
    })
  }

  delete(post: Post, item: PostItem, postIndex: number, itemIndex: number) {
    this.postService.delete(post.shortcode, item.index).subscribe( _ => {
      if (post.items.length == 1) {
        this.posts.splice(postIndex, 1);
      } else {
        post.items.splice(itemIndex, 1);
      }
    })
  }
}
