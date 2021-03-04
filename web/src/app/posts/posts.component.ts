import { Component, OnInit, Optional } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { switchMap } from 'rxjs/operators';

import { Post, PostItem, PostService } from '../services/post.service';
import { ProfileService } from '../services/profile.service';


@Component({
  selector: 'app-posts',
  templateUrl: './posts.component.html',
  styleUrls: ['./posts.component.scss']
})
export class PostsComponent implements OnInit {
  postService: PostService;
  profileService: ProfileService;

  loading = false;
  username$: Observable<string>;
  posts: Post[] = [];
  
  constructor(private route: ActivatedRoute, private router: Router, postService: PostService, profileService: ProfileService) {
    this.postService = postService;
    this.profileService = profileService;
    this.username$ = this.route.queryParamMap.pipe(
      switchMap(queryParam => {
        return queryParam.get("username") ?? ""
      })
    );
  }

  ngOnInit(): void {
    this.loadNext()
  }

  loadNext() {
    if (this.loading) { return }
    this.loading = true;
    this.postService.list(this.posts.length, 20).subscribe( response_data => {
      this.posts.push(...response_data.posts);
      this.loading = false;
    })
  }

  selectedProfileChanged(profile_username: string) {
    this.router.navigate(['/posts'], { queryParams: { profile: profile_username} })
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
